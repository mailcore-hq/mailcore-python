"""Protocolo HTTP real: a API sintética exige TLS válido e registra efeitos.

O prazo configurado é de inatividade por etapa HTTPX. A aplicação pode impor
prazo total ao fluxo assíncrono com asyncio.timeout; essa política é testada à
parte do timeout de leitura do cliente.
"""

from __future__ import annotations

import asyncio
import gzip
import json
import os
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from contextvars import ContextVar
from copy import deepcopy
from urllib.parse import parse_qsl, urlsplit

from servidor_https import ServidorHttpsSintetico

from mailcore import Cliente, ClienteAsync
from mailcore.erros import ErroApi, ErroConfiguracao, ErroResposta, ErroTransporte
from mailcore.recursos import (
    Emails,
    EmailsAsync,
    Modelos,
    ModelosAsync,
    Recebimento,
    RecebimentoAsync,
)
from mailcore.transporte import Transporte, TransporteAsync

CHAVE = "mc_sintetica_123"


class _Canal:
    def __init__(self, transporte, assincrono: bool) -> None:
        self.transporte = transporte
        self.assincrono = assincrono

    async def executar(self, *argumentos, **opcoes):
        if self.assincrono:
            return await self.transporte.executar(*argumentos, **opcoes)
        return self.transporte.executar(*argumentos, **opcoes)

    @asynccontextmanager
    async def fluxo(self, *argumentos, **opcoes):
        if self.assincrono:
            async with self.transporte.fluxo(*argumentos, formato="fluxo", **opcoes) as leitor:
                yield _Leitor(leitor, True)
        else:
            with self.transporte.fluxo(*argumentos, formato="fluxo", **opcoes) as leitor:
                yield _Leitor(leitor, False)


class _Leitor:
    def __init__(self, original, assincrono: bool) -> None:
        self.original = original
        self.assincrono = assincrono

    async def __aiter__(self):
        if self.assincrono:
            async for parte in self.original:
                yield parte
        else:
            for parte in self.original:
                yield parte


@asynccontextmanager
async def canal(servidor, assincrono: bool, **opcoes):
    configuracao = {
        "chave_api": CHAVE,
        "url_base": servidor.url_base(),
        "certificado_ca": servidor.certificado_ca,
        "tempo_limite": 2,
        "tempo_conexao": 1,
    } | opcoes
    transporte = (TransporteAsync if assincrono else Transporte)(**configuracao)
    try:
        yield _Canal(transporte, assincrono)
    finally:
        if assincrono:
            await transporte.fechar()
        else:
            transporte.fechar()


CENARIOS = []


def cenario(funcao):
    CENARIOS.append(funcao)
    return funcao


@cenario
async def json_idempotencia_e_cabecalhos_preservam_null_false_e_unicode(teste, assincrono):
    with ServidorHttpsSintetico() as servidor:
        dados = {
            "remetente": "origem@example.test",
            "destinatarios": ["destino@example.test"],
            "assunto": "Ação",
            "texto": "Olá",
            "tags": {"pedido": "123"},
            "responder_para": None,
            "valor_booleano": False,
        }
        copia = deepcopy(dados)
        async with canal(servidor, assincrono) as cliente:
            resposta = await cliente.executar(
                "POST",
                "/emails",
                corpo=dados,
                chave_idempotencia="pedido-123",
                cabecalhos={"X-Correlacao": "sintetica"},
            )
        teste.assertEqual({"id": "email-sintetico", "estado": "aceita"}, resposta.dados)
        teste.assertEqual(200, resposta.status)
        registro = servidor.registros[0]
        teste.assertEqual("POST", registro["metodo"])
        teste.assertEqual("/v1/emails", registro["alvo"])
        teste.assertEqual("Bearer " + CHAVE, registro["cabecalhos"]["authorization"])
        teste.assertEqual("pedido-123", registro["cabecalhos"]["idempotency-key"])
        teste.assertEqual("sintetica", registro["cabecalhos"]["x-correlacao"])
        teste.assertEqual("application/json", registro["cabecalhos"]["content-type"])
        teste.assertEqual("identity", registro["cabecalhos"]["accept-encoding"])
        teste.assertTrue(registro["cabecalhos"]["user-agent"].startswith("mailcore-python/"))
        teste.assertNotIn("cookie", registro["cabecalhos"])
        teste.assertEqual(copia, json.loads(registro["corpo"]))
        teste.assertEqual(copia, dados)


@cenario
async def filtros_e_segmentos_nao_mudam_a_origem(teste, assincrono):
    with ServidorHttpsSintetico() as servidor:
        async with canal(servidor, assincrono) as cliente:
            emails = (EmailsAsync if assincrono else Emails)(cliente.transporte)
            retorno = emails.obter("parte/ação+?@example.test")
            if assincrono:
                await retorno
            await cliente.executar(
                "GET",
                "/receiving",
                consulta={
                    "busca": "ação+teste & assunto=?",
                    "ativo": False,
                    "limite": 2,
                    "omitido": None,
                },
            )
        teste.assertEqual(
            "/v1/emails/parte%2Fa%C3%A7%C3%A3o%2B%3F%40example.test", servidor.registros[0]["alvo"]
        )
        url = urlsplit(servidor.registros[1]["alvo"])
        teste.assertEqual("/v1/receiving", url.path)
        teste.assertEqual(
            {"busca": "ação+teste & assunto=?", "ativo": "false", "limite": "2"},
            dict(parse_qsl(url.query)),
        )


@cenario
async def chaves_dinamicas_isolam_threads_ou_tasks_por_requisicao(teste, assincrono):
    contexto = ContextVar("chave_sintetica", default=None)
    local = threading.local()
    chave = (lambda: contexto.get()) if assincrono else (lambda: local.chave)
    with ServidorHttpsSintetico() as servidor:
        async with canal(servidor, assincrono, chave_api=chave) as cliente:
            if assincrono:

                async def tarefa(indice):
                    ator = f"ator-{indice}"
                    token = contexto.set("mc_" + ator)
                    try:
                        for _ in range(2):
                            await cliente.executar("GET", "/domains", cabecalhos={"X-Ator": ator})
                    finally:
                        contexto.reset(token)

                await asyncio.gather(*(tarefa(indice) for indice in range(8)))
            else:

                def tarefa(indice):
                    ator = f"ator-{indice}"
                    local.chave = "mc_" + ator
                    try:
                        for _ in range(2):
                            cliente.transporte.executar(
                                "GET", "/domains", cabecalhos={"X-Ator": ator}
                            )
                    finally:
                        del local.chave

                with ThreadPoolExecutor(max_workers=8) as executor:
                    list(executor.map(tarefa, range(8)))
        teste.assertEqual(16, len(servidor.registros))
        for registro in servidor.registros:
            ator = registro["cabecalhos"]["x-ator"]
            teste.assertEqual("Bearer mc_" + ator, registro["cabecalhos"]["authorization"])


@cenario
async def erro_da_chave_e_sanitizado_antes_de_qualquer_http(teste, assincrono):
    segredo = "credencial-sintetica-na-excecao"

    def resolver():
        raise RuntimeError(segredo)

    with ServidorHttpsSintetico() as servidor:
        async with canal(servidor, assincrono, chave_api=resolver) as cliente:
            with teste.assertRaises(ErroConfiguracao) as capturado:
                await cliente.executar("GET", "/domains")
            teste.assertNotIn(segredo, str(capturado.exception))
            teste.assertNotIn(segredo, repr(capturado.exception))
            teste.assertIsNone(capturado.exception.__cause__)
            teste.assertNotIn(CHAVE, repr(cliente.transporte))
        teste.assertEqual([], servidor.registros)


@cenario
async def tls_recusa_ca_ausente_e_ca_incorreta(teste, assincrono):
    outra_ca, _ = ServidorHttpsSintetico.identidade("outra")
    with ServidorHttpsSintetico() as servidor:
        for certificado in (None, str(outra_ca)):
            async with canal(servidor, assincrono, certificado_ca=certificado) as cliente:
                with teste.assertRaises(ErroTransporte) as capturado:
                    await cliente.executar("GET", "/domains")
                teste.assertEqual("falha_de_rede", capturado.exception.codigo)
                teste.assertIsNone(capturado.exception.__cause__)
                teste.assertNotIn(CHAVE, repr(capturado.exception))
        teste.assertEqual([], servidor.registros)
        async with canal(servidor, assincrono) as cliente:
            teste.assertEqual(200, (await cliente.executar("GET", "/domains")).status)


@cenario
async def tls_confere_hostname_mesmo_com_ca_confiavel(teste, assincrono):
    with ServidorHttpsSintetico() as servidor:
        async with canal(servidor, assincrono, url_base=servidor.url_base("localhost")) as cliente:
            with teste.assertRaises(ErroTransporte) as capturado:
                await cliente.executar("GET", "/domains")
            teste.assertEqual("falha_de_rede", capturado.exception.codigo)
        teste.assertEqual([], servidor.registros)


@cenario
async def https_obrigatorio_e_base_sem_dados_embutidos(teste, assincrono):
    classe = TransporteAsync if assincrono else Transporte
    for url in (
        "http://127.0.0.1:9999/v1",
        "http://api.example.test/v1",
        "ftp://example.test/v1",
        "https://usuario:senha@example.test/v1",
        "https://example.test/v1?chave=valor",
        "https://example.test/v1#segredo",
    ):
        with teste.assertRaises(ErroConfiguracao):
            classe(chave_api=CHAVE, url_base=url)
    with teste.assertRaises(ErroConfiguracao):
        classe(chave_api=CHAVE, url_base="http://api.example.test/v1", permitir_http_local=True)


@cenario
async def proxies_do_ambiente_nao_recebem_a_chave(teste, assincrono):
    nomes = ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY")
    antigos = {nome: os.environ.get(nome) for nome in nomes}
    try:
        for nome in nomes:
            os.environ[nome] = "http://127.0.0.1:1"
        with ServidorHttpsSintetico() as servidor:
            async with canal(servidor, assincrono) as cliente:
                teste.assertEqual(200, (await cliente.executar("GET", "/domains")).status)
            teste.assertEqual(1, len(servidor.registros))
    finally:
        for nome, valor in antigos.items():
            if valor is None:
                os.environ.pop(nome, None)
            else:
                os.environ[nome] = valor


@cenario
async def cabecalhos_reservados_e_idempotencia_invalida_sao_recusados(teste, assincrono):
    with ServidorHttpsSintetico() as servidor:
        async with canal(servidor, assincrono) as cliente:
            for nome in (
                "Authorization",
                "Proxy-Authorization",
                "Host",
                "Cookie",
                "Content-Length",
                "Content-Type",
                "Idempotency-Key",
                "Accept",
                "Accept-Encoding",
                "User-Agent",
            ):
                with teste.assertRaises(ErroConfiguracao):
                    await cliente.executar("GET", "/domains", cabecalhos={nome: "valor"})
            for cabecalhos in ({"X-Teste": "valor\r\nAuthorization: teste"}, {"X\nTeste": "valor"}):
                with teste.assertRaises(ErroConfiguracao):
                    await cliente.executar("GET", "/domains", cabecalhos=cabecalhos)
            for chave in ("", "com espaco", "quebra\nlinha", "a" * 257):
                with teste.assertRaises(ErroConfiguracao):
                    await cliente.executar("GET", "/domains", chave_idempotencia=chave)
        teste.assertEqual([], servidor.registros)


@cenario
async def cookies_nao_sao_reutilizados_e_metadados_privados_sao_omitidos(teste, assincrono):
    def atender(pedido):
        pedido.enviar(
            corpo={"id": "sintetico"},
            cabecalhos={
                "Set-Cookie": "sessao=sintetica; Path=/",
                "Authorization": "Bearer nao-retornar",
                "Proxy-Authorization": "nao-retornar",
                "X-Request-Id": "requisicao-sintetica",
            },
        )

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            for _ in range(2):
                resposta = await cliente.executar("GET", "/domains")
                teste.assertEqual("requisicao-sintetica", resposta.cabecalhos["x-request-id"])
                for nome in ("set-cookie", "authorization", "proxy-authorization"):
                    teste.assertNotIn(nome, resposta.cabecalhos)
                with teste.assertRaises(TypeError):
                    resposta.cabecalhos["mutacao"] = "proibida"
        teste.assertEqual(2, len(servidor.registros))
        teste.assertTrue(
            all("cookie" not in registro["cabecalhos"] for registro in servidor.registros)
        )


@cenario
async def conexao_http11_e_reaproveitada_por_cliente(teste, assincrono):
    with ServidorHttpsSintetico() as servidor:
        async with canal(servidor, assincrono) as cliente:
            for _ in range(3):
                teste.assertEqual(200, (await cliente.executar("GET", "/domains")).status)
        teste.assertEqual(3, len(servidor.registros))
        teste.assertEqual(1, len({registro["conexao"] for registro in servidor.registros}))


@cenario
async def cliente_publico_encerra_pool_pelo_contexto_e_recusa_pedidos_apos_fechar(
    teste, assincrono
):
    with ServidorHttpsSintetico() as servidor:
        configuracao = {
            "chave_api": CHAVE,
            "url_base": servidor.url_base(),
            "certificado_ca": servidor.certificado_ca,
        }
        if assincrono:
            async with ClienteAsync(**configuracao) as cliente:
                teste.assertEqual(200, (await cliente.dominios.listar()).status)
            await cliente.fechar()
            await cliente.fechar_async()
            with teste.assertRaises(ErroConfiguracao):
                await cliente.dominios.listar()
        else:
            with Cliente(**configuracao) as cliente:
                teste.assertEqual(200, cliente.dominios.listar().status)
            cliente.fechar()
            with teste.assertRaises(ErroConfiguracao):
                cliente.dominios.listar()
        teste.assertEqual(1, len(servidor.registros))


@cenario
async def json_de_sucesso_malformado_ou_constante_nao_json_e_recusado(teste, assincrono):
    for corpo in (b'{"id":', b'{"numero":NaN}', b"\xff"):

        def atender(pedido, conteudo=corpo):
            pedido.enviar(corpo=conteudo, cabecalhos={"Content-Type": "application/json"})

        with ServidorHttpsSintetico(atender) as servidor:
            async with canal(servidor, assincrono) as cliente:
                with teste.assertRaises(ErroResposta) as capturado:
                    await cliente.executar("GET", "/emails")
                teste.assertEqual("resposta_invalida", capturado.exception.codigo)
                teste.assertEqual(200, capturado.exception.status)
                teste.assertIsNone(capturado.exception.__cause__)


@cenario
async def vazio_204_e_200_seguem_o_contrato_explicito(teste, assincrono):
    def atender(pedido):
        pedido.enviar(status=204 if pedido.path.endswith("/sem-conteudo") else 200)

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            resposta = await cliente.executar("DELETE", "/sem-conteudo")
            teste.assertEqual(204, resposta.status)
            teste.assertIsNone(resposta.dados)
            with teste.assertRaises(ErroResposta):
                await cliente.executar("GET", "/vazio")
            resposta = await cliente.executar("POST", "/vazio", aceitar_vazio=True)
            teste.assertEqual(200, resposta.status)
            teste.assertIsNone(resposta.dados)


@cenario
async def bytes_mime_e_texto_utf8_preservam_conteudo_e_metadados(teste, assincrono):
    dados = b"From: origem@example.test\r\nSubject: sintetico\r\n\r\n\x00\xff\xfe\r\n"

    def atender(pedido):
        if pedido.path.endswith("/raw"):
            pedido.enviar(
                corpo=dados,
                cabecalhos={
                    "Content-Type": "message/rfc822",
                    "Content-Disposition": 'attachment; filename="mensagem.eml"',
                },
            )
        else:
            pedido.enviar(
                corpo="<p>Ação e revisão</p>",
                cabecalhos={"Content-Type": "text/html; charset=utf-8"},
            )

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            recebimento = (RecebimentoAsync if assincrono else Recebimento)(cliente.transporte)
            modelos = (ModelosAsync if assincrono else Modelos)(cliente.transporte)
            resposta = recebimento.baixar_original("email")
            texto = modelos.obter_previa("organizacao", "previa") if not assincrono else None
            if assincrono:
                resposta = await resposta
                texto = await modelos.obter_previa("organizacao", "previa")
            teste.assertEqual(dados, resposta.dados)
            teste.assertIsInstance(resposta.dados, bytes)
            teste.assertEqual("message/rfc822", resposta.cabecalhos["content-type"])
            teste.assertEqual(
                'attachment; filename="mensagem.eml"', resposta.cabecalhos["content-disposition"]
            )
            teste.assertEqual("<p>Ação e revisão</p>", texto.dados)


@cenario
async def codificacao_nao_negociada_e_recusada_sem_descomprimir(teste, assincrono):
    def atender(pedido):
        pedido.enviar(
            corpo=gzip.compress(b"dado-sintetico"), cabecalhos={"Content-Encoding": "gzip"}
        )

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            with teste.assertRaises(ErroResposta) as capturado:
                await cliente.executar("GET", "/receiving/email/raw", formato="bytes")
            teste.assertEqual("codificacao_inesperada", capturado.exception.codigo)
            teste.assertEqual(1, len(servidor.registros))


@cenario
async def inatividade_na_leitura_dispara_timeout_sem_repetir(teste, assincrono):
    def atender(pedido):
        pedido.iniciar_fluxo(**{"X-Request-Id": "prazo-sintetico"})
        pedido.parte(b"primeira")
        time.sleep(0.4)
        pedido.parte(b"segunda")
        pedido.finalizar_fluxo()

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            inicio = time.monotonic()
            with teste.assertRaises(ErroTransporte) as capturado:
                await cliente.executar("GET", "/lento", formato="bytes", tempo_limite=0.15)
            teste.assertEqual("prazo_excedido", capturado.exception.codigo)
            teste.assertEqual("prazo-sintetico", capturado.exception.cabecalhos["x-request-id"])
            teste.assertLess(time.monotonic() - inicio, 1.2)
            teste.assertEqual(1, len(servidor.registros))


@cenario
async def atividade_em_partes_pode_ultrapassar_o_valor_configurado_por_etapa(teste, assincrono):
    def atender(pedido):
        pedido.iniciar_fluxo()
        for _ in range(4):
            pedido.parte(b"parte")
            time.sleep(0.08)
        pedido.finalizar_fluxo()

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            inicio = time.monotonic()
            resposta = await cliente.executar("GET", "/ativo", formato="bytes", tempo_limite=0.2)
            teste.assertEqual(b"parte" * 4, resposta.dados)
            teste.assertGreater(time.monotonic() - inicio, 0.2)


@cenario
async def content_length_excedido_recusa_a_resposta_antes_de_entregar_parte(teste, assincrono):
    def atender(pedido):
        pedido.enviar(corpo=b"a" * 128)

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            partes = []
            with teste.assertRaises(ErroResposta) as capturado:
                async with cliente.fluxo("GET", "/grande", limite_resposta_bytes=16) as leitor:
                    partes = [parte async for parte in leitor]
            teste.assertEqual("resposta_excedida", capturado.exception.codigo)
            teste.assertEqual([], partes)


@cenario
async def fluxo_sem_content_length_respeita_o_limite_real(teste, assincrono):
    def atender(pedido):
        pedido.iniciar_fluxo()
        for _ in range(3):
            pedido.parte(b"12345")
        pedido.finalizar_fluxo()

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            partes = []
            with teste.assertRaises(ErroResposta) as capturado:
                async with cliente.fluxo("GET", "/fluxo", limite_resposta_bytes=10) as leitor:
                    async for parte in leitor:
                        partes.append(parte)
            teste.assertEqual("resposta_excedida", capturado.exception.codigo)
            teste.assertLessEqual(len(b"".join(partes)), 10)


@cenario
async def consumidor_recebe_primeira_parte_antes_do_final_da_resposta(teste, assincrono):
    liberar = threading.Event()

    def atender(pedido):
        pedido.iniciar_fluxo()
        pedido.parte(b"primeira")
        if liberar.wait(1):
            pedido.parte(b"segunda")
            pedido.finalizar_fluxo()
        else:
            pedido.desconectar()

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono) as cliente:
            async with cliente.fluxo("GET", "/fluxo") as leitor:
                partes = []
                async for parte in leitor:
                    partes.append(parte)
                    if len(partes) == 1:
                        liberar.set()
                teste.assertEqual(200, leitor.original.status)
                teste.assertEqual(15, leitor.original.total_bytes)
            teste.assertEqual(b"primeirasegunda", b"".join(partes))
            teste.assertGreaterEqual(len(partes), 2)


@cenario
async def erro_do_consumidor_encerra_fluxo_e_libera_pool(teste, assincrono):
    def atender(pedido):
        if pedido.path.endswith("/fluxo"):
            pedido.iniciar_fluxo()
            pedido.parte(b"primeira")
            time.sleep(0.2)
            pedido.parte(b"segunda")
            pedido.finalizar_fluxo()
        else:
            pedido.enviar(corpo={"id": "apos-cancelamento"})

    class CancelamentoConsumidor(RuntimeError):
        pass

    original = CancelamentoConsumidor("cancelamento sintético")
    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono, maximo_conexoes=1, conexoes_ociosas=1) as cliente:
            with teste.assertRaises(CancelamentoConsumidor) as capturado:
                async with cliente.fluxo("GET", "/fluxo") as leitor:
                    async for _parte in leitor:
                        raise original
            teste.assertIs(original, capturado.exception)
            resposta = await cliente.executar("GET", "/ok", tempo_limite=0.4)
            teste.assertEqual("apos-cancelamento", resposta["id"])
            teste.assertEqual(2, len(servidor.registros))


@cenario
async def break_antecipado_e_saida_do_contexto_liberam_a_conexao(teste, assincrono):
    def atender(pedido):
        if pedido.path.endswith("/fluxo"):
            pedido.iniciar_fluxo()
            pedido.parte(b"primeira")
            time.sleep(0.2)
            pedido.parte(b"segunda")
            pedido.finalizar_fluxo()
        else:
            pedido.enviar(corpo={"id": "apos-break"})

    with ServidorHttpsSintetico(atender) as servidor:
        async with canal(servidor, assincrono, maximo_conexoes=1, conexoes_ociosas=1) as cliente:
            partes = []
            async with cliente.fluxo("GET", "/fluxo") as leitor:
                async for parte in leitor:
                    partes.append(parte)
                    break
            teste.assertEqual(1, len(partes))
            resposta = await cliente.executar("GET", "/ok", tempo_limite=0.4)
            teste.assertEqual("apos-break", resposta["id"])
            teste.assertEqual(2, len(servidor.registros))


@cenario
async def json_escapado_maior_que_csv_nao_usa_limite_de_8_mib(teste, assincrono):
    with ServidorHttpsSintetico() as servidor:
        conteudo = (
            'email,primeiro_nome\nusuario@example.test,"' + ('""' * (2 * 1024 * 1024 + 64)) + '"\n'
        )
        teste.assertLess(len(conteudo.encode()), 8 * 1024 * 1024)
        async with canal(servidor, assincrono, tempo_limite=10) as cliente:
            resposta = await cliente.executar(
                "POST",
                "/contacts/imports",
                corpo={
                    "arquivo_nome": "contatos.csv",
                    "conteudo": conteudo,
                    "mapeamento": {"0": "email", "1": "primeiro_nome"},
                },
            )
            teste.assertEqual(200, resposta.status)
        registro = servidor.registros[0]
        teste.assertGreater(len(registro["corpo"]), 8 * 1024 * 1024)
        teste.assertEqual(conteudo, json.loads(registro["corpo"])["conteudo"])


@cenario
async def json_acima_de_50_mib_e_recusado_antes_da_rede(teste, assincrono):
    with ServidorHttpsSintetico() as servidor:
        async with canal(servidor, assincrono) as cliente:
            with teste.assertRaises(ErroConfiguracao):
                await cliente.executar(
                    "POST", "/contacts/imports", corpo={"conteudo": "x" * (50 * 1024 * 1024)}
                )
        teste.assertEqual([], servidor.registros)


@cenario
async def valores_json_invalidos_e_opcoes_booleanas_nao_chegam_a_rede(teste, assincrono):
    with ServidorHttpsSintetico() as servidor:
        async with canal(servidor, assincrono) as cliente:
            for valor in (
                float("nan"),
                float("inf"),
                float("-inf"),
                object(),
                complex(1, 2),
                "\udfff",
            ):
                with teste.assertRaises(ErroConfiguracao):
                    await cliente.executar("POST", "/events/send", corpo={"valor": valor})
            for dados in ({1: "valor"}, {"\udfff": "valor"}):
                with teste.assertRaises(ErroConfiguracao):
                    await cliente.executar("POST", "/events/send", corpo=dados)
            for opcoes in (
                {"tempo_limite": True},
                {"tempo_limite": False},
                {"limite_resposta_bytes": True},
                {"limite_resposta_bytes": False},
            ):
                with teste.assertRaises(ErroConfiguracao):
                    await cliente.executar("GET", "/domains", **opcoes)
        teste.assertEqual([], servidor.registros)


for _codigo in (401, 403, 409, 422, 429, 500, 503):
    for _json in (False, True):

        async def erro_http(teste, assincrono, codigo=_codigo, usar_json=_json):
            def atender(pedido):
                corpo = (
                    {"erro": {"codigo": "recusada", "mensagem": "Pedido sintético recusado."}}
                    if usar_json
                    else "<html>detalhe-privado-sintetico</html>"
                )
                pedido.enviar(
                    status=codigo,
                    corpo=corpo,
                    cabecalhos={
                        "Retry-After": "7",
                        "X-Request-Id": "requisicao-sintetica",
                        "Set-Cookie": "sessao=sintetica",
                        "Authorization": "nao-retornar",
                    },
                )

            with ServidorHttpsSintetico(atender) as servidor:
                async with canal(servidor, assincrono) as cliente:
                    with teste.assertRaises(ErroApi) as capturado:
                        await cliente.executar("POST", "/emails", corpo={"texto": "teste"})
                    erro = capturado.exception
                    teste.assertEqual(codigo, erro.status)
                    teste.assertEqual("recusada" if usar_json else "erro_http", erro.codigo)
                    teste.assertEqual("7", erro.cabecalhos["retry-after"])
                    teste.assertEqual("requisicao-sintetica", erro.cabecalhos["x-request-id"])
                    teste.assertNotIn("set-cookie", erro.cabecalhos)
                    teste.assertNotIn("authorization", erro.cabecalhos)
                    teste.assertNotIn("detalhe-privado-sintetico", str(erro))
                    teste.assertEqual(1, len(servidor.registros))

        erro_http.__name__ = f"erro_http_{_codigo}_{'json' if _json else 'html'}_sem_retry"
        CENARIOS.append(erro_http)


for _codigo in (301, 302, 307, 308):

    async def redirecionamento(teste, assincrono, codigo=_codigo):
        with ServidorHttpsSintetico() as destino:

            def atender(pedido):
                pedido.enviar(
                    status=codigo,
                    corpo="redirecionado",
                    cabecalhos={"Location": destino.url_base() + "/capturar"},
                )

            with ServidorHttpsSintetico(atender) as origem:
                async with canal(origem, assincrono) as cliente:
                    with teste.assertRaises(ErroApi) as capturado:
                        await cliente.executar("POST", "/emails", corpo={"texto": "sintetico"})
                    teste.assertEqual("redirecionamento_recusado", capturado.exception.codigo)
                    teste.assertEqual(codigo, capturado.exception.status)
                    teste.assertEqual(1, len(origem.registros))
                    teste.assertEqual([], destino.registros)

    redirecionamento.__name__ = f"redirecionamento_{_codigo}_nao_e_seguido"
    CENARIOS.append(redirecionamento)


for _metodo in ("GET", "POST"):

    async def queda(teste, assincrono, metodo=_metodo):
        def atender(pedido):
            pedido.desconectar()

        with ServidorHttpsSintetico(atender) as servidor:
            async with canal(servidor, assincrono) as cliente:
                with teste.assertRaises(ErroTransporte) as capturado:
                    await cliente.executar(
                        metodo,
                        "/emails",
                        corpo={"texto": "sintetico"} if metodo == "POST" else None,
                    )
                teste.assertEqual("falha_de_rede", capturado.exception.codigo)
                teste.assertEqual(1, len(servidor.registros))

    queda.__name__ = f"queda_apos_{_metodo.lower()}_nao_dispara_retry"
    CENARIOS.append(queda)


for _formato, _moldura, _conteudo in (
    ("json", "tamanho", b'{"id":"parcial"}'),
    ("bytes", "tamanho", b"From: origem@example.test\r\n\r\nMIME parcial"),
    ("fluxo", "tamanho", b"email,nome\r\nusuario@example.test,Parcial\r\n"),
    ("bytes", "chunked", b"From: origem@example.test\r\n\r\nMIME parcial"),
    ("fluxo", "chunked", b"email,nome\r\nusuario@example.test,Parcial\r\n"),
):

    async def truncada(teste, assincrono, formato=_formato, moldura=_moldura, conteudo=_conteudo):
        def atender(pedido):
            if moldura == "tamanho":
                pedido.cabecalhos(**{"Content-Length": "500", "Connection": "close"})
                pedido.wfile.write(conteudo)
                pedido.wfile.flush()
            else:
                pedido.iniciar_fluxo()
                pedido.wfile.write(b"1f4\r\n" + conteudo)
                pedido.wfile.flush()
            pedido.desconectar()

        with ServidorHttpsSintetico(atender) as servidor:
            async with canal(servidor, assincrono) as cliente:
                with teste.assertRaises(ErroTransporte) as capturado:
                    if formato == "fluxo":
                        async with cliente.fluxo("GET", "/truncada") as leitor:
                            _ = [parte async for parte in leitor]
                    else:
                        await cliente.executar("GET", "/truncada", formato=formato)
                teste.assertIn(capturado.exception.codigo, {"falha_de_rede", "resposta_incompleta"})
                teste.assertEqual(1, len(servidor.registros))

    truncada.__name__ = f"resposta_truncada_{_formato}_{_moldura}_nao_e_sucesso"
    CENARIOS.append(truncada)


class TestesTransporteSync(unittest.TestCase):
    pass


class TestesTransporteAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # A serialização dos cenários de 50 MiB é trabalho síncrono deliberado.
        asyncio.get_running_loop().slow_callback_duration = 2

    async def test_cancelamento_de_task_ou_prazo_da_aplicacao_libera_o_pool(self):
        def atender(pedido):
            if pedido.path.endswith("/fluxo"):
                pedido.iniciar_fluxo()
                pedido.parte(b"primeira")
                time.sleep(0.6)
                pedido.parte(b"segunda")
                pedido.finalizar_fluxo()
            else:
                pedido.enviar(corpo={"id": "apos-task"})

        with ServidorHttpsSintetico(atender) as servidor:
            async with canal(servidor, True, maximo_conexoes=1, conexoes_ociosas=1) as cliente:
                consumido = asyncio.Event()

                async def leitura():
                    async with cliente.fluxo("GET", "/fluxo") as leitor:
                        async for _parte in leitor:
                            consumido.set()

                tarefa = asyncio.create_task(leitura())
                try:
                    await asyncio.wait_for(consumido.wait(), 1)
                    tarefa.cancel()
                    with self.assertRaises(asyncio.CancelledError):
                        await tarefa
                finally:
                    if not tarefa.done():
                        tarefa.cancel()
                        await asyncio.gather(tarefa, return_exceptions=True)
                self.assertEqual(
                    "apos-task", (await cliente.executar("GET", "/ok", tempo_limite=0.4))["id"]
                )
                with self.assertRaises(TimeoutError):
                    async with asyncio.timeout(0.15):
                        async with cliente.fluxo("GET", "/fluxo") as leitor:
                            _ = [parte async for parte in leitor]
                self.assertEqual(
                    "apos-task", (await cliente.executar("GET", "/ok", tempo_limite=0.4))["id"]
                )
                self.assertEqual(4, len(servidor.registros))


def caso_sync(funcao):
    def verificar(self):
        asyncio.run(funcao(self, False))

    return verificar


def caso_async(funcao):
    async def verificar(self):
        await funcao(self, True)

    return verificar


for _funcao in CENARIOS:
    setattr(TestesTransporteSync, "test_" + _funcao.__name__, caso_sync(_funcao))
    setattr(TestesTransporteAsync, "test_" + _funcao.__name__, caso_async(_funcao))


if __name__ == "__main__":
    unittest.main()
