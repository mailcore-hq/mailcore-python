"""Roteamento real dos frameworks com I/O do SDK substituído no boot."""

import asyncio
import json
import unittest
from collections.abc import AsyncIterator
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

import django
import httpx
from django.test import Client as ClienteTesteDjango
from django.test import override_settings
from django.urls import path

from exemplos.compartilhado import LIMITE_CORPO, configurar, validar_cabecalhos
from exemplos.django_app import criar_view
from exemplos.fastapi_app import criar_aplicacao as criar_fastapi
from exemplos.flask_app import criar_aplicacao as criar_flask
from mailcore import ErroApi, ErroTransporte


class ClienteSintetico:
    def __init__(self) -> None:
        self.emails = self
        self.pedidos: list[tuple[dict, dict]] = []
        self.tentativas = 0
        self.falha: Exception | None = None
        self.dados = {"id": "email-sintetico", "estado": "aceita", "privado": "nao-publicar"}
        self.fechamentos = 0
        self.execucao_async = False

    def registrar(self, pedido: dict, opcoes: dict) -> SimpleNamespace:
        self.tentativas += 1
        if self.falha:
            raise self.falha
        self.pedidos.append((pedido, opcoes))
        return SimpleNamespace(
            dados=self.dados, status=202, cabecalhos={"x-privado": "nao-publicar"}
        )

    def enviar(self, pedido: dict, **opcoes: object) -> SimpleNamespace:
        return self.registrar(pedido, opcoes)

    def fechar(self) -> None:
        self.fechamentos += 1


class ClienteAsyncSintetico(ClienteSintetico):
    async def enviar(self, pedido: dict, **opcoes: object) -> SimpleNamespace:
        self.execucao_async = asyncio.current_task() is not None
        await asyncio.sleep(0)
        return self.registrar(pedido, opcoes)

    async def fechar_async(self) -> None:
        self.fechamentos += 1


class TestesExemplos(unittest.IsolatedAsyncioTestCase):
    TOKEN = "aplicacao_sintetica_" + "Ab9_" * 12
    CHAVE = "mc_" + "chave_sintetica_" * 4
    FRAMEWORKS = ("flask", "fastapi", "django")

    @classmethod
    def setUpClass(cls) -> None:
        from django.conf import settings

        if not settings.configured:
            settings.configure(
                SECRET_KEY="chave-sintetica-exclusiva-dos-testes-de-framework",
                ALLOWED_HOSTS=["testserver", "aplicacao.example.test"],
                INSTALLED_APPS=[],
                MIDDLEWARE=["django.middleware.csrf.CsrfViewMiddleware"],
                DATA_UPLOAD_MAX_MEMORY_SIZE=LIMITE_CORPO,
                DEBUG=False,
            )
            django.setup()

    def ambiente(self) -> dict[str, str]:
        return {
            "MAILCORE_API_KEY": self.CHAVE,
            "TOKEN_APLICACAO": self.TOKEN,
            "MAILCORE_REMETENTE": "Equipe <origem@example.test>",
            "MAILCORE_DESTINATARIO": "destino@example.test",
        }

    def cabecalhos(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.TOKEN}",
            "Idempotency-Key": "pedido-sintetico-1",
            "Content-Type": "application/json",
        }

    async def chamar(
        self,
        framework: str,
        cliente: ClienteSintetico,
        *,
        corpo: bytes = b"{}",
        cabecalhos: dict[str, str] | None = None,
        metodo: str = "POST",
        caminho: str = "/enviar",
    ) -> httpx.Response:
        recebidos = self.cabecalhos() if cabecalhos is None else cabecalhos
        if framework == "fastapi":
            aplicacao = criar_fastapi(ambiente=self.ambiente(), cliente=cliente)
            async with aplicacao.router.lifespan_context(aplicacao):
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=aplicacao),
                    base_url="https://aplicacao.example.test",
                ) as http:
                    return await http.request(metodo, caminho, content=corpo, headers=recebidos)
        if framework == "flask":
            aplicacao = criar_flask(ambiente=self.ambiente(), cliente=cliente)
            with aplicacao.test_client() as http:
                resposta = http.open(caminho, method=metodo, data=corpo, headers=recebidos)
                return httpx.Response(
                    resposta.status_code, headers=resposta.headers, content=resposta.data
                )
        rotas = ModuleType("rotas_sinteticas_mailcore")
        rotas.urlpatterns = [path("enviar", criar_view(ambiente=self.ambiente(), cliente=cliente))]
        with override_settings(ROOT_URLCONF=rotas):
            http = ClienteTesteDjango(enforce_csrf_checks=True)
            resposta = http.generic(metodo, caminho, data=corpo, headers=recebidos)
            return httpx.Response(
                resposta.status_code, headers=dict(resposta.headers), content=resposta.content
            )

    def cliente(self, framework: str) -> ClienteSintetico:
        return ClienteAsyncSintetico() if framework == "fastapi" else ClienteSintetico()

    def conferir_sanitizacao(self, resposta: httpx.Response) -> None:
        for segredo in (self.TOKEN, self.CHAVE, "nao-publicar"):
            self.assertNotIn(segredo, resposta.text)
            self.assertNotIn(segredo, str(resposta.headers))

    async def test_aceitacao_real_em_todos_os_frameworks(self) -> None:
        for framework in self.FRAMEWORKS:
            with self.subTest(framework=framework):
                cliente = self.cliente(framework)
                resposta = await self.chamar(framework, cliente)
                self.assertEqual(202, resposta.status_code)
                self.assertEqual({"id": "email-sintetico", "estado": "aceita"}, resposta.json())
                self.assertEqual("no-store", resposta.headers["cache-control"])
                self.assertEqual(1, cliente.tentativas)
                self.assertEqual(0, cliente.fechamentos)
                self.assertEqual(framework == "fastapi", cliente.execucao_async)
                self.conferir_sanitizacao(resposta)

    async def test_corpo_e_query_maliciosos_nao_configuram_o_envio(self) -> None:
        corpo = json.dumps(
            {
                "remetente": "outro@example.test",
                "destinatarios": ["terceiro@example.test"],
                "texto": "Não usar",
                "cliente": {},
                "chave_api": "outra",
                "url_base": "https://outro.invalid",
            }
        ).encode()
        for framework in self.FRAMEWORKS:
            cliente = self.cliente(framework)
            resposta = await self.chamar(
                framework, cliente, corpo=corpo, caminho="/enviar?destinatario=outro"
            )
            self.assertEqual(202, resposta.status_code)
            pedido, opcoes = cliente.pedidos[0]
            self.assertEqual("Equipe <origem@example.test>", pedido["remetente"])
            self.assertEqual(["destino@example.test"], pedido["destinatarios"])
            self.assertEqual("Integração Mailcore com Python.", pedido["texto"])
            self.assertEqual({"chave_idempotencia": "pedido-sintetico-1"}, opcoes)

    async def test_token_ausente_api_key_e_cabecalho_ambiguo_nao_enviam(self) -> None:
        for framework in self.FRAMEWORKS:
            for token in (
                "",
                "Bearer curto",
                f"Bearer {self.CHAVE}",
                f"Bearer {self.TOKEN},Bearer {self.TOKEN}",
            ):
                cliente = self.cliente(framework)
                resposta = await self.chamar(
                    framework, cliente, cabecalhos={**self.cabecalhos(), "Authorization": token}
                )
                self.assertEqual(401, resposta.status_code)
                self.assertEqual(0, cliente.tentativas)
                self.conferir_sanitizacao(resposta)

    async def test_idempotencia_e_externa_obrigatoria_e_estavel(self) -> None:
        for framework in self.FRAMEWORKS:
            for chave in ("", "com espaco", "a,b", "a" * 257):
                cliente = self.cliente(framework)
                resposta = await self.chamar(
                    framework, cliente, cabecalhos={**self.cabecalhos(), "Idempotency-Key": chave}
                )
                self.assertEqual(400, resposta.status_code)
                self.assertEqual(0, cliente.tentativas)
            cliente = self.cliente(framework)
            for _ in range(2):
                self.assertEqual(202, (await self.chamar(framework, cliente)).status_code)
            self.assertEqual(2, cliente.tentativas)
            self.assertEqual(
                ["pedido-sintetico-1"] * 2,
                [opcoes["chave_idempotencia"] for _, opcoes in cliente.pedidos],
            )

    async def test_json_codificacao_tipo_e_limite_sao_validados(self) -> None:
        for framework in self.FRAMEWORKS:
            for corpo in (b"", b"{", b"[]", b"true", b'{"texto":"\xff"}', b'{"numero":NaN}'):
                cliente = self.cliente(framework)
                resposta = await self.chamar(framework, cliente, corpo=corpo)
                self.assertEqual(400, resposta.status_code, (framework, corpo))
                self.assertEqual(0, cliente.tentativas)
            cliente = self.cliente(framework)
            resposta = await self.chamar(framework, cliente, corpo=b"x" * (LIMITE_CORPO + 1))
            self.assertEqual(413, resposta.status_code)
            resposta = await self.chamar(
                framework, cliente, cabecalhos={**self.cabecalhos(), "Content-Type": "text/plain"}
            )
            self.assertEqual(415, resposta.status_code)
            self.assertEqual(0, cliente.tentativas)

    async def test_api_e_transporte_nao_expoem_detalhes_nem_repetem(self) -> None:
        for framework in self.FRAMEWORKS:
            for erro, status in (
                (
                    ErroApi(
                        self.CHAVE,
                        codigo="validacao",
                        status=422,
                        cabecalhos={"authorization": self.CHAVE},
                    ),
                    422,
                ),
                (ErroApi(self.CHAVE, codigo="redirecionamento_recusado", status=302), 502),
                (ErroTransporte(self.TOKEN), 502),
            ):
                cliente = self.cliente(framework)
                cliente.falha = erro
                resposta = await self.chamar(framework, cliente)
                self.assertEqual(status, resposta.status_code)
                self.assertEqual(1, cliente.tentativas)
                self.conferir_sanitizacao(resposta)

    async def test_resposta_incompleta_e_metodos_nao_previstos(self) -> None:
        for framework in self.FRAMEWORKS:
            cliente = self.cliente(framework)
            cliente.dados = {"id": None, "estado": "aceita"}
            self.assertEqual(502, (await self.chamar(framework, cliente)).status_code)
            cliente = self.cliente(framework)
            self.assertEqual(405, (await self.chamar(framework, cliente, metodo="GET")).status_code)
            self.assertEqual(
                404, (await self.chamar(framework, cliente, caminho="/outra")).status_code
            )
            self.assertEqual(0, cliente.tentativas)

    def test_configuracao_insegura_falha_no_boot_e_duplicados_sao_recusados(self) -> None:
        for token in (None, "curto", 123, self.CHAVE, self.TOKEN + ",duplicado"):
            with self.assertRaises(ValueError):
                configurar({**self.ambiente(), "TOKEN_APLICACAO": token})
        with self.assertRaises(Exception) as falha:
            validar_cabecalhos(
                configurar(self.ambiente()),
                [f"Bearer {self.TOKEN}"] * 2,
                ["pedido"],
                "application/json",
            )
        self.assertEqual(401, falha.exception.status)

    async def test_fastapi_fecha_somente_o_cliente_que_criou(self) -> None:
        cliente = ClienteAsyncSintetico()
        with patch("exemplos.fastapi_app.ClienteAsync", return_value=cliente):
            aplicacao = criar_fastapi(ambiente=self.ambiente())
            async with aplicacao.router.lifespan_context(aplicacao):
                self.assertIs(cliente, aplicacao.state.cliente_mailcore)
            self.assertEqual(1, cliente.fechamentos)

    async def test_fastapi_interrompe_stream_sem_content_length_ao_exceder_o_limite(self) -> None:
        cliente = ClienteAsyncSintetico()
        aplicacao = criar_fastapi(ambiente=self.ambiente(), cliente=cliente)
        partes_lidas = 0

        async def corpo_virtual() -> AsyncIterator[bytes]:
            nonlocal partes_lidas
            for _ in range(1024 * 1024):
                partes_lidas += 1
                yield b"x" * 1024

        async with aplicacao.router.lifespan_context(aplicacao):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=aplicacao),
                base_url="https://aplicacao.example.test",
            ) as http:
                resposta = await http.post(
                    "/enviar", content=corpo_virtual(), headers=self.cabecalhos()
                )
        self.assertEqual(413, resposta.status_code)
        self.assertEqual(5, partes_lidas)
        self.assertEqual(0, cliente.tentativas)


if __name__ == "__main__":
    unittest.main()
