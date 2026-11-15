"""Cliente de integração em Docker; relatórios não contêm credenciais ou conteúdo."""

from __future__ import annotations

import asyncio
import base64
import json
import platform
import ssl
import sys
import tempfile
import time
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from mailcore import Cliente, ClienteAsync, Erro, ErroApi


class FalhaIntegracao(Exception):
    pass


def exigir(condicao: bool) -> None:
    if not condicao:
        raise FalhaIntegracao


def esperar_erro(status: int, executar: Any) -> None:
    try:
        executar()
    except ErroApi as erro:
        exigir(erro.status == status)
        return
    raise FalhaIntegracao


def agendamento() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()


class IntegracaoApi:
    def __init__(self, fixture: dict[str, Any], certificado: str) -> None:
        self.fixture = fixture
        self.certificado = certificado
        self.etapa = "prontidao"
        self.cenarios: list[str] = []

    def opcoes(self, chave: str) -> dict[str, Any]:
        return {
            "chave_api": chave,
            "url_base": "https://mailcore-api:3443/v1",
            "certificado_ca": self.certificado,
            "tempo_limite": 10,
        }

    def concluir(self, cenario: str) -> None:
        self.cenarios.append(cenario)

    async def conferir_envio_async(self, chave: str, pedido: dict[str, Any], aceita: Any) -> None:
        async with ClienteAsync(**self.opcoes(chave)) as cliente:
            resposta = await cliente.emails.enviar(pedido, chave_idempotencia="python-composto")
            exigir(resposta.status == 202 and resposta.dados == aceita)
            exigir(chave not in repr(cliente) and chave not in repr(resposta))

    async def conferir_mime_async(self, chave: str, recebido: str, mime: bytes) -> None:
        async with ClienteAsync(**self.opcoes(chave)) as cliente:
            resposta = await cliente.recebimento.baixar_original(recebido)
            exigir(isinstance(resposta.dados, bytes) and resposta.dados == mime)
            async with cliente.recebimento.baixar_original_fluxo(recebido) as fluxo:
                partes = [parte async for parte in fluxo]
                exigir(fluxo.status == 200 and fluxo.total_bytes == len(mime))
                exigir(fluxo.cabecalhos["content-type"] == "message/rfc822")
            exigir(b"".join(partes) == mime)

    def executar(self) -> dict[str, Any]:
        try:
            with ExitStack() as recursos:
                api = recursos.enter_context(
                    httpx.Client(
                        base_url="https://mailcore-api:3443",
                        verify=ssl.create_default_context(cafile=self.certificado),
                        trust_env=False,
                        follow_redirects=False,
                        timeout=3,
                    )
                )
                return self.executar_cenarios(recursos, api)
        except Exception as erro:
            return {
                "resultado": "falhou",
                "python": platform.python_version(),
                "etapa": self.etapa,
                "cenarios": self.cenarios,
                "erro_http": {"codigo": erro.codigo, "status": erro.status}
                if isinstance(erro, Erro)
                else None,
                "falha": "Contrato de integração não satisfeito; detalhes privados omitidos.",
            }

    def executar_cenarios(self, recursos: ExitStack, api: httpx.Client) -> dict[str, Any]:
        fim = time.monotonic() + 30
        pronta = False
        while not pronta and time.monotonic() < fim:
            try:
                pronta = api.get("/health/ready").status_code == 200
            except httpx.RequestError:
                pass
            if not pronta:
                time.sleep(0.2)
        exigir(pronta)

        self.etapa = "criar_full_sessao_sintetica"
        criacao = api.post(
            "/v1/api-keys",
            headers={
                "Origin": "https://localhost:17443",
                "Cookie": "__Host-mailcore=" + self.fixture.pop("token"),
                "X-CSRF-Token": self.fixture.pop("csrf"),
            },
            json={"nome": "Fixture Python Full", "permissao": "full_access"},
        )
        exigir(criacao.status_code == 201)
        full = criacao.json()
        sdk = recursos.enter_context(Cliente(**self.opcoes(full["chave"])))
        remetente = "avisos@" + self.fixture["nome_dominio"]

        self.etapa = "chaves_full_sending_escopo_repr"
        chave_envio = sdk.chaves_api.criar(
            {
                "nome": "Fixture Python Sending",
                "permissao": "sending_access",
                "dominio_id": self.fixture["dominio"],
            }
        ).dados
        envio = recursos.enter_context(Cliente(**self.opcoes(chave_envio["chave"])))
        esperar_erro(403, lambda: envio.dominios.listar())
        exigir(full["chave"] not in repr(sdk))
        exigir(
            any(
                chave["id"] == chave_envio["id"] for chave in sdk.chaves_api.listar().dados["dados"]
            )
        )
        self.concluir(self.etapa)

        pedido = {
            "remetente": f"Equipe Python <{remetente}>",
            "destinatarios": ["principal@example.test"],
            "cc": ["copia@example.test"],
            "cco": ["oculto@example.test"],
            "assunto": "Validação Python",
            "texto": "Dados sintéticos",
            "html": '<p>Dados sintéticos<img src="cid:marca@example.test"></p>',
            "cabecalhos": {"X-Teste-SDK": "sintetico"},
            "agendada_em": agendamento(),
            "anexos": [
                {
                    "nome": "marca.png",
                    "tipo_conteudo": "image/png",
                    "conteudo_base64": base64.b64encode(bytes([137, 80, 78, 71])).decode(),
                    "id_conteudo": "marca@example.test",
                }
            ],
        }
        self.etapa = "envio_composto_idempotencia_409_download_cancelamento"
        resposta_aceita = envio.emails.enviar(pedido, chave_idempotencia="python-composto")
        aceita = resposta_aceita.dados
        exigir(resposta_aceita.status == 202 and aceita["estado"] == "agendada")
        exigir(envio.emails.enviar(pedido, chave_idempotencia="python-composto").dados == aceita)
        esperar_erro(
            409,
            lambda: envio.emails.enviar(
                {**pedido, "assunto": "Outra intenção"}, chave_idempotencia="python-composto"
            ),
        )
        exigir(sdk.emails.obter_por_idempotencia("python-composto")["id"] == aceita["id"])
        exigir(len(sdk.emails.obter(aceita["id"]).dados["destinatarios"]) == 3)
        anexo = sdk.emails.baixar_anexo(aceita["id"], 0).dados
        exigir(isinstance(anexo, bytes) and anexo == bytes([137, 80, 78, 71]))
        self.concluir(self.etapa)

        self.etapa = "envio_async_replay_mesma_intencao"
        asyncio.run(self.conferir_envio_async(chave_envio["chave"], pedido, aceita))
        exigir(sdk.emails.cancelar(aceita["id"]).dados["estado"] == "cancelada")
        self.concluir(self.etapa)

        self.etapa = "lote_atomico_repeticao_conflito"
        item = {
            "remetente": remetente,
            "destinatarios": ["lote@example.test"],
            "assunto": "Lote Python",
            "texto": "Dados sintéticos",
            "agendada_em": agendamento(),
        }
        antes = sorted(email["id"] for email in sdk.emails.listar({"limite": 100}).dados["dados"])
        esperar_erro(
            422,
            lambda: envio.lotes.enviar(
                [item, {**item, "destinatarios": ["endereco-invalido"]}],
                chave_idempotencia="python-lote-invalido",
            ),
        )
        depois = sorted(email["id"] for email in sdk.emails.listar({"limite": 100}).dados["dados"])
        exigir(antes == depois)
        lote = [item, {**item, "assunto": "Segundo item Python"}]
        aceita_lote = envio.lotes.enviar(lote, chave_idempotencia="python-lote").dados
        exigir(len(aceita_lote["dados"]) == 2)
        exigir(envio.lotes.enviar(lote, chave_idempotencia="python-lote").dados == aceita_lote)
        exigir(sdk.lotes.obter_por_idempotencia("python-lote").dados == aceita_lote)
        esperar_erro(
            409,
            lambda: envio.lotes.enviar(
                [{**item, "assunto": "Divergente"}, lote[-1]], chave_idempotencia="python-lote"
            ),
        )
        exigir(len(sdk.emails.listar({"limite": 100}).dados["dados"]) == len(antes) + 2)
        for email in aceita_lote["dados"]:
            sdk.emails.cancelar(email["id"])
        self.concluir(self.etapa)

        self.etapa = "dominios_capacidades_tracking_crud"
        dominio = sdk.dominios.atualizar(
            self.fixture["dominio"],
            {
                "capacidades": {"envio": "enabled", "recebimento": "enabled"},
                "rastreamento_aberturas": True,
                "rastreamento_cliques": True,
            },
        ).dados
        exigir(
            dominio["capacidades"]["recebimento"] == "enabled"
            and dominio["rastreamento_aberturas"] is True
        )
        novo = sdk.dominios.criar(
            {
                "nome": "python-" + self.fixture["organizacao"].replace("-", "") + ".example.com",
                "capacidades": {"envio": "enabled", "recebimento": "disabled"},
            }
        ).dados
        exigir(sdk.dominios.remover(novo["id"])["estado"] == "suspenso")
        self.concluir(self.etapa)

        self.etapa = "contatos_nulos_catalogos_exportacao_csv_fluxo"
        segmento = sdk.segmentos.criar({"nome": "Segmento Python"}).dados
        topico = sdk.topicos.criar(
            {"nome": "Tópico Python", "visibilidade": "publico", "assinatura_padrao": "opt_in"}
        ).dados
        contato = sdk.contatos.criar(
            {
                "email": "contato@example.test",
                "primeiro_nome": "Sintético",
                "segmentos": [segmento["id"]],
                "topicos": [{"id": topico["id"], "assinatura": "opt_in"}],
            }
        ).dados
        exigir(sdk.contatos.obter(contato["id"])["id"] == contato["id"])
        exigir(
            sdk.contatos.atualizar(contato["id"], {"primeiro_nome": None})["primeiro_nome"] is None
        )
        exportacao = sdk.contatos.exportacoes.criar(
            {}, chave_idempotencia="python-exportacao"
        ).dados
        exigir(exportacao["estado"] == "concluida" and exportacao["total"] == 1)
        with sdk.contatos.exportacoes.baixar_fluxo(exportacao["id"]) as fluxo:
            csv = b"".join(fluxo)
            exigir(fluxo.status == 200 and fluxo.total_bytes == len(csv))
        exigir(b"contato@example.test" in csv)
        exigir(
            any(
                item["id"] == exportacao["id"]
                for item in sdk.contatos.exportacoes.listar().dados["dados"]
            )
        )
        self.concluir(self.etapa)

        self.etapa = "modelos_pastas_versoes_previa_publicacao_cas"
        pasta = sdk.modelos.pastas.criar({"nome": "Pasta Python"}).dados
        modelo = sdk.modelos.criar(
            {
                "nome": "Modelo Python",
                "html": "<p>Olá, {{{NOME}}}.</p>",
                "pasta_id": pasta["id"],
                "remetente": remetente,
                "assunto": "Modelo sintético",
                "variaveis": [{"chave": "NOME", "tipo": "string"}],
            }
        ).dados
        versao = sdk.modelos.versoes.listar(modelo["id"]).dados["dados"][0]
        versao_obtida = sdk.modelos.versoes.obter(modelo["id"], versao["id"]).dados
        exigir(versao_obtida["versao_id"] == versao["id"] and versao_obtida["id"] == modelo["id"])
        previa = sdk.modelos.prever(
            modelo["id"], {"revisao": modelo["revisao"], "variaveis": {"NOME": "Python"}}
        ).dados
        exigir("Python" in previa["html"])
        previa_id = urlparse(previa["url"]).path.split("/")[-1]
        exigir("Python" in sdk.modelos.obter_previa(self.fixture["organizacao"], previa_id).dados)
        antiga = modelo["revisao"]
        modelo = sdk.modelos.atualizar(
            modelo["id"], {"revisao": antiga, "nome": "Modelo editado"}
        ).dados
        esperar_erro(
            409,
            lambda: sdk.modelos.atualizar(modelo["id"], {"revisao": antiga, "nome": "Conflito"}),
        )
        modelo = sdk.modelos.publicar(modelo["id"], {"revisao": modelo["revisao"]}).dados
        exigir(modelo["status"] == "published")
        modelo = sdk.modelos.versoes.restaurar(
            modelo["id"], versao["id"], {"revisao": modelo["revisao"]}
        ).dados
        self.concluir(self.etapa)

        self.etapa = "marketing_crud_sem_disparo"
        campanha = sdk.campanhas.criar({"nome": "Campanha Python"}).dados
        campanha = sdk.campanhas.atualizar(
            campanha["id"], {"revisao": campanha["revisao"], "nome": "Campanha editada"}
        ).dados
        exigir(sdk.campanhas.obter(campanha["id"])["id"] == campanha["id"])
        sdk.campanhas.remover(campanha["id"])
        evento = sdk.eventos.criar(
            {"nome": "python.qa", "esquema": {"pontos": "number", "ativo": "boolean"}}
        ).dados
        exigir(sdk.eventos.atualizar(evento["id"], {"esquema": None})["esquema"] is None)
        automacao = sdk.automacoes.criar({"nome": "Automação Python", "estado": "inativa"}).dados
        automacao = sdk.automacoes.atualizar(
            automacao["id"], {"revisao": automacao["revisao"], "nome": "Automação editada"}
        ).dados
        exigir(sdk.automacoes.obter(automacao["id"])["id"] == automacao["id"])
        sdk.automacoes.remover(automacao["id"])
        sdk.eventos.remover(evento["id"])
        self.concluir(self.etapa)

        self.etapa = "caixas_etiquetas_rascunhos_cas_sem_envio"
        caixa = sdk.caixas.criar(
            {"endereco": "suporte@" + self.fixture["nome_dominio"], "nome": "Suporte Python"}
        ).dados
        exigir(sdk.caixas.obter(caixa["id"])["id"] == caixa["id"])
        etiqueta = sdk.caixas.etiquetas.criar(
            caixa["id"], {"nome": "Pedidos", "cor": "#224466"}
        ).dados
        rascunho = sdk.caixas.rascunhos.criar(
            caixa["id"], {"para": ["cliente@example.test"], "assunto": "Pedido", "texto": "Olá"}
        ).dados
        antiga = rascunho["revisao"]
        rascunho = sdk.caixas.rascunhos.atualizar(
            caixa["id"], rascunho["id"], {"revisao": antiga, "texto": "Atualizado"}
        ).dados
        esperar_erro(
            409,
            lambda: sdk.caixas.rascunhos.atualizar(
                caixa["id"], rascunho["id"], {"revisao": antiga, "texto": "Conflito"}
            ),
        )
        exigir(sdk.caixas.rascunhos.obter(caixa["id"], rascunho["id"])["html"] is None)
        sdk.caixas.rascunhos.remover(caixa["id"], rascunho["id"])
        sdk.caixas.etiquetas.remover(caixa["id"], etiqueta["id"])
        sdk.caixas.remover(caixa["id"])
        self.concluir(self.etapa)

        self.etapa = "recebimento_mime_real_pendente_bytes_fluxo"
        exigir(not sdk.recebimento.listar().dados["dados"])
        caminho = "/interno/postal/recebidos/" + self.fixture["rota"]
        cabecalhos = {
            "Content-Type": "application/json",
            "X-Postal-Signature-256": self.fixture.pop("callback_assinatura"),
        }
        corpo_callback = self.fixture.pop("callback_corpo").encode()
        callback = api.post(caminho, headers=cabecalhos, content=corpo_callback)
        exigir(callback.status_code == 200)
        recebido = callback.json()["id"]
        repetida = api.post(caminho, headers=cabecalhos, content=corpo_callback)
        exigir(repetida.status_code == 200 and repetida.json()["id"] == recebido)
        mime = base64.b64decode(self.fixture.pop("mime_esperado"), validate=True)
        detalhe = sdk.recebimento.obter(recebido, {"formato_html": "cid"}).dados
        exigir(
            detalhe["estado_processamento"] == "pendente"
            and detalhe["para"] == ["real@" + self.fixture["nome_dominio"]]
        )
        original = sdk.recebimento.baixar_original(recebido)
        exigir(original.status == 200 and original.cabecalhos["content-type"] == "message/rfc822")
        exigir(isinstance(original.dados, bytes) and original.dados == mime)
        with sdk.recebimento.baixar_original_fluxo(recebido) as fluxo:
            bruto = b"".join(fluxo)
            exigir(fluxo.status == 200 and fluxo.total_bytes == len(mime))
        exigir(bruto == mime)
        exigir(len(sdk.recebimento.listar().dados["dados"]) == 1)
        esperar_erro(403, lambda: envio.recebimento.listar())
        self.concluir(self.etapa)

        self.etapa = "recebimento_async_bytes_contexto_fluxo"
        asyncio.run(self.conferir_mime_async(full["chave"], recebido, mime))
        self.concluir(self.etapa)

        self.etapa = "cli_revogacao_e_limpeza_crud"
        exigir(not sdk.cli.concessoes.listar({"limite": 1}).dados["dados"])
        esperar_erro(403, lambda: envio.cli.concessoes.listar())
        respostas = [
            sdk.contatos.remover(contato["id"]),
            sdk.segmentos.remover(segmento["id"]),
            sdk.topicos.remover(topico["id"]),
            sdk.modelos.remover(modelo["id"]),
            sdk.modelos.pastas.remover(pasta["id"]),
            sdk.chaves_api.revogar(chave_envio["id"]),
        ]
        exigir(all(200 <= resposta.status <= 299 for resposta in respostas))
        esperar_erro(401, lambda: envio.emails.enviar(pedido, chave_idempotencia="python-revogada"))
        self.concluir(self.etapa)
        return {
            "resultado": "aprovado",
            "python": platform.python_version(),
            "httpx": httpx.__version__,
            "cenarios": self.cenarios,
            "recebimento_processado_por_worker": False,
            "async_exercitado": True,
            "async_envio_repetiu_intencao_existente": True,
        }


def main() -> int:
    try:
        dados = json.loads(sys.stdin.buffer.read())
        with tempfile.TemporaryDirectory(prefix="mailcore-python-ca-") as pasta:
            certificado = Path(pasta) / "ca.crt"
            certificado.write_text(dados.pop("certificado_ca"), encoding="ascii")
            certificado.chmod(0o600)
            resultado = IntegracaoApi(dados, str(certificado)).executar()
    except Exception:
        resultado = {
            "resultado": "falhou",
            "etapa": "configuracao",
            "falha": "Não foi possível iniciar o cliente sintético.",
        }
    print(json.dumps(resultado, ensure_ascii=False))
    return 0 if resultado["resultado"] == "aprovado" else 1


if __name__ == "__main__":
    sys.exit(main())
