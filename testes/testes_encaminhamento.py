"""Encaminhamento completo, limitado e sem consultas a URLs do recebido."""

import asyncio
import base64
import hashlib
import json
import unittest
from copy import deepcopy

import httpx
from servidor_https import ServidorHttpsSintetico

from mailcore import Cliente, ClienteAsync, ErroApi, ErroConfiguracao, ErroResposta, ErroTransporte

MAXIMO_ANEXOS = 5 * 1024 * 1024
PEDIDO = {
    "recebido_id": "recebido",
    "remetente": "Equipe São Paulo <equipe@example.test>",
    "destinatarios": ["pessoa@example.test"],
}


class Cenario:
    def __init__(self):
        self.pedidos = []
        self.arquivos = {"pdf": b"%PDF-1.7\r\n\xff", "png": b"\x89PNG\r\n\x1a\n"}
        self.raw = b"From: original@example.test\r\nSubject: A\r\n\r\nCorpo\xff\x00\r\n"
        self.detalhe = {
            "conteudo_disponivel": True,
            "estado_processamento": "concluida",
            "formato_html": "cid",
            "assunto": "Ação São Paulo",
            "texto": "Texto com ação",
            "html": '<p>Ação<img src="cid:logo@example.test"><img src="https://invalido.test/a">',
            "anexos": [
                {
                    "id": "pdf",
                    "nome": "ação.pdf",
                    "tipo_conteudo": "application/pdf",
                    "tamanho": len(self.arquivos["pdf"]),
                    "id_conteudo": None,
                },
                {
                    "id": "png",
                    "nome": "anexo-2",
                    "tipo_conteudo": "image/png",
                    "tamanho": len(self.arquivos["png"]),
                    "id_conteudo": "logo@example.test",
                },
            ],
            "raw_download_url": "https://invalido.test/segredo?token=confidencial",
            "remetente": "original@example.test",
            "cc": ["copia@example.test"],
            "cco": ["oculto@example.test"],
            "cabecalhos": [["X-Confidencial", "nao-copiar"]],
            "responder_para": ["outro@example.test"],
            "message_id": "original-id",
        }
        for anexo in self.detalhe["anexos"]:
            anexo["download_url"] = "https://invalido.test/arquivo?token=confidencial"
        self.respostas = {}

    def responder(self, pedido):
        self.pedidos.append(pedido)
        if pedido.url.host != "mailcore.com.br":
            raise AssertionError("Origem inesperada")
        if pedido.url.path in self.respostas:
            resposta = self.respostas[pedido.url.path]
            if isinstance(resposta, BaseException):
                raise resposta
            if resposta.is_stream_consumed:
                return httpx.Response(
                    resposta.status_code, headers=resposta.headers, content=resposta.content
                )
            return resposta
        if pedido.method == "POST":
            if pedido.url.path != "/v1/emails":
                raise AssertionError("Rota de envio inesperada")
            return httpx.Response(202, json={"id": "novo-id", "estado": "aceita"})
        if pedido.url.path == "/v1/receiving/recebido":
            if pedido.url.query != b"formato_html=cid":
                raise AssertionError("Formato incorreto")
            return httpx.Response(200, json=self.detalhe)
        if pedido.url.path == "/v1/receiving/recebido/raw":
            return httpx.Response(200, content=self.raw)
        for id_anexo, conteudo in self.arquivos.items():
            if pedido.url.path == f"/v1/receiving/recebido/attachments/{id_anexo}/download":
                return httpx.Response(200, content=conteudo)
        raise AssertionError("Rota de leitura inesperada")

    def envios(self):
        return [pedido for pedido in self.pedidos if pedido.method == "POST"]

    def downloads(self):
        return [
            pedido for pedido in self.pedidos if pedido.url.path.endswith(("/raw", "/download"))
        ]


def conferir_preservado(teste, cenario, resposta):
    teste.assertEqual(resposta.dados, {"id": "novo-id", "estado": "aceita"})
    teste.assertEqual(len(cenario.pedidos), 4)
    corpo = json.loads(cenario.envios()[0].content)
    teste.assertEqual(
        set(corpo), {"remetente", "destinatarios", "assunto", "texto", "html", "anexos"}
    )
    for campo in ("remetente", "destinatarios"):
        teste.assertEqual(corpo[campo], PEDIDO[campo])
    for campo in ("assunto", "texto", "html"):
        teste.assertEqual(corpo[campo], cenario.detalhe[campo])
    for entrada, anexo in zip(cenario.detalhe["anexos"], corpo["anexos"], strict=True):
        teste.assertEqual(anexo["nome"], entrada["nome"])
        teste.assertEqual(anexo["tipo_conteudo"], entrada["tipo_conteudo"])
        teste.assertEqual(anexo.get("id_conteudo"), entrada["id_conteudo"])
        teste.assertEqual(
            base64.b64decode(anexo["conteudo_base64"]), cenario.arquivos[entrada["id"]]
        )
    for pedido in cenario.pedidos:
        teste.assertEqual(pedido.headers["authorization"], "Bearer mc_sintetica")
        teste.assertNotIn("confidencial", str(pedido.url))
        teste.assertEqual(pedido.headers["X-Correlacao"], "sintetica")
        teste.assertEqual(pedido.extensions["timeout"]["read"], 2.5)
        if pedido.method == "GET":
            teste.assertNotIn("idempotency-key", pedido.headers)
        else:
            teste.assertEqual(pedido.headers["idempotency-key"], "intencao-exata")


OPCOES = {
    "chave_idempotencia": "intencao-exata",
    "tempo_limite": 2.5,
    "cabecalhos": {"X-Correlacao": "sintetica"},
}


class TestesEncaminhamento(unittest.TestCase):
    def test_preserva_conteudo_arquivos_cid_nome_sem_extensao_e_novo_envelope(self):
        cenario = Cenario()
        pedido = deepcopy(PEDIDO)
        opcoes = deepcopy(OPCOES)
        with Cliente(
            "mc_sintetica", transporte_http=httpx.MockTransport(cenario.responder)
        ) as cliente:
            resposta = cliente.recebimento.encaminhar(pedido, **opcoes)
        self.assertEqual(pedido, PEDIDO)
        self.assertEqual(opcoes, OPCOES)
        conferir_preservado(self, cenario, resposta)

    def test_eml_preserva_bytes_exatos_corpo_e_assunto_sem_duplicar_prefixo(self):
        for assunto, esperado in [
            ("Ação", "Fwd: Ação"),
            ("fWd: Ação", "fWd: Ação"),
            (None, "Fwd: Sem assunto"),
            ("", "Fwd: Sem assunto"),
        ]:
            with self.subTest(assunto=assunto):
                cenario = Cenario()
                cenario.detalhe["assunto"] = assunto
                cenario.detalhe["anexos"] = [{"tipo_conteudo": "application/zip"}]
                pedido = dict(
                    PEDIDO, preservar_conteudo=False, texto="Meu corpo", html="<p>Meu corpo"
                )
                with Cliente(
                    "mc_sintetica", transporte_http=httpx.MockTransport(cenario.responder)
                ) as cliente:
                    cliente.recebimento.encaminhar(pedido, **OPCOES)
                corpo = json.loads(cenario.envios()[0].content)
                self.assertEqual(corpo["assunto"], esperado)
                self.assertEqual(corpo["texto"], "Meu corpo")
                self.assertEqual(corpo["html"], "<p>Meu corpo")
                self.assertEqual(len(cenario.downloads()), 1)
                anexo = corpo["anexos"][0]
                self.assertEqual(set(anexo), {"nome", "tipo_conteudo", "conteudo_base64"})
                self.assertEqual(anexo["nome"], "mensagem-encaminhada.eml")
                self.assertEqual(anexo["tipo_conteudo"], "message/rfc822")
                self.assertEqual(
                    hashlib.sha256(base64.b64decode(anexo["conteudo_base64"])).digest(),
                    hashlib.sha256(cenario.raw).digest(),
                )
                self.assertNotIn("idempotency-key", cenario.downloads()[0].headers)

    def test_intencao_estavel_e_timeout_do_post_nao_gera_repeticao(self):
        cenario = Cenario()
        with Cliente(
            "mc_sintetica", transporte_http=httpx.MockTransport(cenario.responder)
        ) as cliente:
            for _ in range(2):
                cliente.recebimento.encaminhar(PEDIDO, **OPCOES)
            self.assertEqual(cenario.envios()[0].content, cenario.envios()[1].content)
            cenario.respostas["/v1/emails"] = httpx.ReadTimeout("nao-reproduzir")
            with self.assertRaises(ErroTransporte):
                cliente.recebimento.encaminhar(PEDIDO, **OPCOES)
        self.assertEqual(len(cenario.envios()), 3)


class TestesEncaminhamentoAsync(unittest.IsolatedAsyncioTestCase):
    async def executar(self, cenario, pedido=PEDIDO, **opcoes):
        async with ClienteAsync(
            "mc_sintetica", transporte_http=httpx.MockTransport(cenario.responder)
        ) as cliente:
            return await cliente.recebimento.encaminhar(pedido, **opcoes)

    async def rejeitar_nas_duas_variantes(
        self, cenario, pedido, erro=ErroConfiguracao, downloads=0
    ):
        for assincrono in (False, True):
            with self.subTest(assincrono=assincrono):
                cenario.pedidos.clear()
                with self.assertRaises(erro) as contexto:
                    if assincrono:
                        await self.executar(cenario, pedido)
                    else:
                        with Cliente(
                            "mc_sintetica", transporte_http=httpx.MockTransport(cenario.responder)
                        ) as cliente:
                            cliente.recebimento.encaminhar(pedido)
                self.assertNotIn("confidencial", str(contexto.exception))
                self.assertEqual(cenario.envios(), [])
                self.assertEqual(len(cenario.downloads()), downloads)

    async def test_async_preserva_mesma_composicao_e_opcoes(self):
        cenario = Cenario()
        resposta = await self.executar(cenario, **OPCOES)
        conferir_preservado(self, cenario, resposta)

    async def test_async_eml_usa_corpo_chamador_e_raw(self):
        cenario = Cenario()
        resposta = await self.executar(
            cenario, dict(PEDIDO, preservar_conteudo=False, html="<p>Ação")
        )
        self.assertEqual(resposta.dados["id"], "novo-id")
        corpo = json.loads(cenario.envios()[0].content)
        self.assertEqual(base64.b64decode(corpo["anexos"][0]["conteudo_base64"]), cenario.raw)
        self.assertNotIn("texto", corpo)

    async def test_recusa_pedidos_incompativeis_antes_de_qualquer_http(self):
        for alteracoes in [
            {"texto": "nao-permitido"},
            {"html": None},
            {"preservar_conteudo": True, "texto": "x"},
            {"preservar_conteudo": False},
            {"preservar_conteudo": False, "texto": "  "},
            {"preservar_conteudo": False, "texto": 1},
            {"preservar_conteudo": 1},
            {"destinatarios": []},
            {"destinatarios": ["p@example.test"] * 51},
            {"destinatarios": ["x\r\nBcc: segredo"]},
            {"remetente": "origem\nprivado"},
            {"recebido_id": ".."},
            {"cc": []},
            {"assunto": "incompativel"},
            {"preservar_conteudo": False, "texto": "á" * (250 * 1024 + 1)},
        ]:
            cenario = Cenario()
            with self.subTest(campos=list(alteracoes)):
                await self.rejeitar_nas_duas_variantes(cenario, dict(PEDIDO, **alteracoes))
                self.assertEqual(cenario.pedidos, [])

    async def test_recusa_indisponibilidade_e_corpos_invalidos_sem_baixar(self):
        for alteracoes in [
            {"conteudo_disponivel": False},
            {"conteudo_disponivel": 1},
            {"estado_processamento": "pendente"},
            {"formato_html": "data_uri"},
            {"texto": None, "html": " "},
            {"texto": 1},
            {"assunto": "injecao\r\nBcc: x"},
            {"assunto": "a" * 2001},
            {"texto": "á" * (250 * 1024), "html": "a"},
        ]:
            cenario = Cenario()
            cenario.detalhe.update(alteracoes)
            await self.rejeitar_nas_duas_variantes(cenario, PEDIDO)

    async def test_valida_todos_metadados_antes_do_primeiro_download(self):
        for alteracoes in [
            {"nome": "programa.exe"},
            {"nome": "logo.jpg"},
            {"nome": "../a.png"},
            {"nome": "a\r\nb.png"},
            {"nome": "a;.png"},
            {"nome": "á" * 128},
            {"nome": " logo.png"},
            {"nome": "anexo", "id_conteudo": None},
            {"tipo_conteudo": "application/zip"},
            {"tamanho": -1},
            {"tamanho": True},
            {"tamanho": MAXIMO_ANEXOS},
            {"id": "pdf"},
            {"id_conteudo": "<cid>"},
            {"id_conteudo": "cid\n"},
            {"id_conteudo": "á"},
            {"id_conteudo": "a" * 513},
            {"nome": "a.eml", "tipo_conteudo": "message/rfc822"},
        ]:
            cenario = Cenario()
            cenario.detalhe["anexos"][1].update(alteracoes)
            await self.rejeitar_nas_duas_variantes(cenario, PEDIDO)
        cenario = Cenario()
        cenario.detalhe["anexos"][0]["id_conteudo"] = "logo@example.test"
        await self.rejeitar_nas_duas_variantes(cenario, PEDIDO)
        for anexos in [None, [{}] * 11]:
            cenario = Cenario()
            cenario.detalhe["anexos"] = anexos
            await self.rejeitar_nas_duas_variantes(cenario, PEDIDO)

    async def test_json_estimado_excedido_recusa_antes_de_download(self):
        cenario = Cenario()
        cenario.detalhe["texto"] = "\0" * (500 * 1024)
        cenario.detalhe["html"] = None
        cenario.detalhe["anexos"] = [dict(cenario.detalhe["anexos"][0], tamanho=MAXIMO_ANEXOS)]
        await self.rejeitar_nas_duas_variantes(cenario, PEDIDO)

    async def test_json_final_eml_excedido_aborta_apos_leitura_sem_post(self):
        cenario = Cenario()
        cenario.raw = b"a" * MAXIMO_ANEXOS
        pedido = dict(PEDIDO, preservar_conteudo=False, texto="\0" * (500 * 1024))
        await self.rejeitar_nas_duas_variantes(cenario, pedido, downloads=1)

    async def test_tamanho_real_divergente_nao_envia_parcial(self):
        for diferenca in (-1, 1):
            cenario = Cenario()
            cenario.detalhe["anexos"][0]["tamanho"] += diferenca
            await self.rejeitar_nas_duas_variantes(cenario, PEDIDO, downloads=1)

    async def test_erro_de_download_ou_redirecionamento_nao_envia_nem_segue_url(self):
        for status in (302, 404, 500):
            cenario = Cenario()
            cenario.respostas["/v1/receiving/recebido/attachments/pdf/download"] = httpx.Response(
                status,
                headers={"Location": "https://invalido.test/confidencial"},
                json={"erro": {"codigo": "arquivo_ausente", "mensagem": "Arquivo indisponível."}},
            )
            await self.rejeitar_nas_duas_variantes(cenario, PEDIDO, ErroApi, downloads=1)

    async def test_raw_acima_de_cinco_mib_e_limite_de_resposta_nao_enviam(self):
        cenario = Cenario()
        cenario.raw = b"a" * (MAXIMO_ANEXOS + 1)
        await self.rejeitar_nas_duas_variantes(
            cenario, dict(PEDIDO, preservar_conteudo=False, texto="x"), ErroResposta, 1
        )
        cenario = Cenario()
        with self.assertRaises(ErroResposta):
            await self.executar(cenario, limite_resposta_bytes=1)
        self.assertEqual(cenario.envios(), [])

    async def test_cancelamento_fecha_fluxo_e_aborta_antes_do_post(self):
        class FluxoCancelado(httpx.AsyncByteStream):
            fechado = False

            async def __aiter__(self):
                yield b"a"
                raise asyncio.CancelledError()

            async def aclose(self):
                self.fechado = True

        cenario = Cenario()
        fluxo = FluxoCancelado()
        cenario.respostas["/v1/receiving/recebido/attachments/pdf/download"] = httpx.Response(
            200, stream=fluxo
        )
        with self.assertRaises(asyncio.CancelledError):
            await self.executar(cenario)
        self.assertTrue(fluxo.fechado)
        self.assertEqual(cenario.envios(), [])

    async def test_erro_http_inicial_e_timeout_post_preservam_erros_sem_retry(self):
        cenario = Cenario()
        cenario.respostas["/v1/receiving/recebido"] = httpx.Response(
            403, json={"erro": {"codigo": "acesso_negado", "mensagem": "Sem acesso."}}
        )
        await self.rejeitar_nas_duas_variantes(cenario, PEDIDO, ErroApi)
        cenario = Cenario()
        cenario.respostas["/v1/emails"] = httpx.ReadTimeout("confidencial")
        with self.assertRaises(ErroTransporte):
            await self.executar(cenario, **OPCOES)
        self.assertEqual(len(cenario.envios()), 1)

    async def test_arquivo_vazio_declarado_e_limites_inclusivos(self):
        cenario = Cenario()
        cenario.arquivos = {str(indice): b"" for indice in range(10)}
        cenario.detalhe["anexos"] = [
            dict(cenario.detalhe["anexos"][0], id=identificador, tamanho=0)
            for identificador in cenario.arquivos
        ]
        cenario.detalhe["texto"] = "a" * (500 * 1024)
        cenario.detalhe["html"] = None
        pedido = dict(PEDIDO, preservar_conteudo=True, destinatarios=["p@example.test"] * 50)
        await self.executar(cenario, pedido)
        self.assertEqual(len(cenario.downloads()), 10)
        self.assertEqual(
            json.loads(cenario.envios()[0].content)["anexos"][0]["conteudo_base64"], ""
        )
        cenario = Cenario()
        cenario.raw = b"a" * MAXIMO_ANEXOS
        await self.executar(cenario, dict(PEDIDO, preservar_conteudo=False, texto="x"))
        self.assertEqual(
            len(
                base64.b64decode(
                    json.loads(cenario.envios()[0].content)["anexos"][0]["conteudo_base64"]
                )
            ),
            MAXIMO_ANEXOS,
        )

    async def test_raw_vazio_opcoes_invalidas_e_assunto_maior_em_bytes_recusam(self):
        cenario = Cenario()
        cenario.raw = b""
        await self.rejeitar_nas_duas_variantes(
            cenario, dict(PEDIDO, preservar_conteudo=False, texto="x"), downloads=1
        )
        for opcoes in [
            {"chave_idempotencia": "nao\nvalida"},
            {"limite_resposta_bytes": True},
            {"limite_resposta_bytes": "1"},
            {"opcao_inventada": True},
        ]:
            cenario = Cenario()
            with self.assertRaises(ErroConfiguracao):
                await self.executar(cenario, **opcoes)
            self.assertEqual(cenario.pedidos, [])
        cenario = Cenario()
        cenario.detalhe["assunto"] = "á" * 500
        await self.rejeitar_nas_duas_variantes(cenario, PEDIDO)


class TestesEncaminhamentoHttps(unittest.IsolatedAsyncioTestCase):
    async def executar_real(self, servidor, assincrono, pedido=PEDIDO, **opcoes):
        configuracao = {"url_base": servidor.url_base(), "certificado_ca": servidor.certificado_ca}
        if assincrono:
            async with ClienteAsync("mc_sintetica", **configuracao) as cliente:
                return await cliente.recebimento.encaminhar(pedido, **opcoes)
        with Cliente("mc_sintetica", **configuracao) as cliente:
            return cliente.recebimento.encaminhar(pedido, **opcoes)

    async def test_https_real_detalhe_cid_downloads_bearer_e_um_post(self):
        for assincrono in (False, True):
            cenario = Cenario()

            def atender(atendimento, cenario=cenario):
                if atendimento.path == "/v1/receiving/recebido?formato_html=cid":
                    atendimento.enviar(corpo=cenario.detalhe)
                elif atendimento.path == "/v1/emails":
                    atendimento.enviar(status=202, corpo={"id": "novo-https", "estado": "aceita"})
                else:
                    identificador = atendimento.path.split("/")[-2]
                    atendimento.enviar(corpo=cenario.arquivos[identificador])

            with self.subTest(assincrono=assincrono), ServidorHttpsSintetico(atender) as servidor:
                resposta = await self.executar_real(servidor, assincrono, **OPCOES)
                self.assertEqual(resposta.dados["id"], "novo-https")
                registros = servidor.registros
                self.assertEqual(
                    [r["alvo"] for r in registros],
                    [
                        "/v1/receiving/recebido?formato_html=cid",
                        "/v1/receiving/recebido/attachments/pdf/download",
                        "/v1/receiving/recebido/attachments/png/download",
                        "/v1/emails",
                    ],
                )
                for registro in registros:
                    self.assertEqual(registro["cabecalhos"]["authorization"], "Bearer mc_sintetica")
                    if registro["metodo"] == "GET":
                        self.assertNotIn("idempotency-key", registro["cabecalhos"])
                self.assertEqual(registros[-1]["cabecalhos"]["idempotency-key"], "intencao-exata")
                corpo = json.loads(registros[-1]["corpo"])
                self.assertEqual(corpo["html"], cenario.detalhe["html"])
                self.assertEqual(
                    base64.b64decode(corpo["anexos"][1]["conteudo_base64"]), cenario.arquivos["png"]
                )

    async def test_https_segundo_download_401_410_aborta_sem_post(self):
        for assincrono in (False, True):
            for status in (401, 410):
                cenario = Cenario()

                def atender(atendimento, cenario=cenario, status=status):
                    if "?formato_html=cid" in atendimento.path:
                        atendimento.enviar(corpo=cenario.detalhe)
                    elif "/pdf/download" in atendimento.path:
                        atendimento.enviar(corpo=cenario.arquivos["pdf"])
                    else:
                        atendimento.enviar(
                            status=status,
                            corpo={
                                "erro": {
                                    "codigo": "origem_indisponivel",
                                    "mensagem": "Origem indisponível.",
                                }
                            },
                        )

                with (
                    self.subTest(assincrono=assincrono, status=status),
                    ServidorHttpsSintetico(atender) as servidor,
                ):
                    with self.assertRaises(ErroApi) as contexto:
                        await self.executar_real(servidor, assincrono, **OPCOES)
                    self.assertEqual(contexto.exception.status, status)
                    self.assertEqual(contexto.exception.codigo, "origem_indisponivel")
                    self.assertEqual(len(servidor.registros), 3)
                    self.assertTrue(all(r["metodo"] == "GET" for r in servidor.registros))

    async def test_https_teto_por_leitura_sem_content_length(self):
        for assincrono in (False, True):
            cenario = Cenario()

            def atender(atendimento, cenario=cenario):
                if "?formato_html=cid" in atendimento.path:
                    atendimento.enviar(corpo=cenario.detalhe)
                else:
                    atendimento.iniciar_fluxo()
                    for _ in range(81):
                        atendimento.parte(b"a" * (64 * 1024))
                    atendimento.finalizar_fluxo()

            with self.subTest(assincrono=assincrono), ServidorHttpsSintetico(atender) as servidor:
                with self.assertRaises(ErroResposta):
                    await self.executar_real(
                        servidor, assincrono, dict(PEDIDO, preservar_conteudo=False, texto="Corpo")
                    )
                self.assertEqual(len(servidor.registros), 2)
                self.assertTrue(all(r["metodo"] == "GET" for r in servidor.registros))
