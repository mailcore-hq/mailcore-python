"""Assinatura interoperável e uso do cliente por adaptadores HTTP públicos."""

import base64
import hashlib
import hmac
import json
import math
import os
import unittest
from unittest.mock import patch

import httpx

from mailcore import (
    Cliente,
    ClienteAsync,
    ErroAssinatura,
    ErroConfiguracao,
    ErroResposta,
    ErroTransporte,
    Resposta,
    verificar_assinatura,
)

SEGREDO = "whsec_Y2hhdmUtc2ludGV0aWNhLTMyLWJ5dGVzLXRlc3RlLTEyMw=="
CORPO = '{"type":"email.received","created_at":"2026-11-14T12:00:00Z","data":{"email_id":"sintetico","texto":"Olá"}}'
CABECALHOS = {
    "svix-id": "evento-sintetico",
    "svix-timestamp": "1794657600",
    "svix-signature": "v1,m9hOSHQVO80Rb70GMzUg63QIVu/RqjtC5MC5rCjISXM=",
}


def verificar(corpo=CORPO, cabecalhos=None, segredo=SEGREDO, agora=1794657600):
    return verificar_assinatura(
        corpo, CABECALHOS if cabecalhos is None else cabecalhos, segredo, agora=agora
    )


class TestesAssinatura(unittest.TestCase):
    def test_vetor_fixo_produzido_por_node_crypto_com_utf8(self):
        self.assertEqual(verificar()["data"]["texto"], "Olá")
        self.assertEqual(verificar(), verificar(CORPO.encode()))

    def test_rotacao_e_cabecalhos_wsgi(self):
        rotacao = CABECALHOS | {
            "svix-signature": "v1,AAAA v0,ignorada " + CABECALHOS["svix-signature"]
        }
        self.assertEqual(verificar(), verificar(cabecalhos=rotacao))
        wsgi = {
            "HTTP_" + nome.upper().replace("-", "_"): valor for nome, valor in CABECALHOS.items()
        }
        self.assertEqual(verificar(), verificar(cabecalhos=wsgi))

    def test_alteracao_e_segredos_invalidos(self):
        for corpo in (
            CORPO + " ",
            CORPO.replace("sintetico", "outro"),
            CORPO.replace("Olá", "Ola"),
        ):
            with self.subTest(corpo=corpo), self.assertRaises(ErroAssinatura):
                verificar(corpo)
        for segredo in ("whsec_???", "outro", "whsec_YQ==", None):
            with self.subTest(segredo=segredo), self.assertRaises(ErroAssinatura):
                verificar(segredo=segredo)

    def test_janela_e_numeros_especiais(self):
        for desvio in (-300, 300):
            self.assertEqual(verificar(agora=1794657600 + desvio)["type"], "email.received")
        for momento in (1794657299, 1794657901, math.nan, math.inf, -math.inf, True):
            with self.subTest(momento=momento), self.assertRaises(ErroAssinatura):
                verificar(agora=momento)
        for instante in ("0", "1794657600x", "-1", "1794657600.0"):
            with self.subTest(instante=instante), self.assertRaises(ErroAssinatura):
                verificar(cabecalhos=CABECALHOS | {"svix-timestamp": instante})

    def test_cabecalho_duplicado_ausente_e_tolerancia_insegura(self):
        for cabecalhos in (
            {},
            CABECALHOS | {"Svix-Id": "outro"},
            CABECALHOS | {"svix-id": "id\r\n"},
        ):
            with self.assertRaises(ErroAssinatura):
                verificar(cabecalhos=cabecalhos)
        for tolerancia in (0, 301, True):
            with self.assertRaises(ErroAssinatura):
                verificar_assinatura(
                    CORPO, CABECALHOS, SEGREDO, agora=1794657600, tolerancia=tolerancia
                )

    def test_envelope_assinado_malformado_e_json_nao_finito(self):
        for corpo in (
            "{}",
            "[]",
            '{"type":"email.received","created_at":"data","data":NaN}',
            '{"type":1,"created_at":"data","data":null}',
        ):
            assinatura = base64.b64encode(
                hmac.digest(
                    base64.b64decode(SEGREDO[6:]),
                    b"evento-sintetico.1794657600." + corpo.encode(),
                    hashlib.sha256,
                )
            ).decode()
            with self.assertRaises(ErroAssinatura):
                verificar(corpo, CABECALHOS | {"svix-signature": "v1," + assinatura})


class TestesAdaptador(unittest.TestCase):
    def test_mock_convencional_e_metadados_sem_conteudo_em_repr(self):
        chamadas = []

        def responder(pedido):
            chamadas.append(pedido)
            return httpx.Response(
                202,
                json={"id": "sintetico", "estado": "aceita"},
                headers={"x-request-id": "consulta", "set-cookie": "nao-guardar=1"},
            )

        with Cliente("mc_sintetica", transporte_http=httpx.MockTransport(responder)) as cliente:
            resposta = cliente.emails.enviar(
                {
                    "remetente": "a@example.test",
                    "destinatarios": ["b@example.test"],
                    "assunto": "Teste",
                    "texto": "Conteúdo",
                }
            )
            self.assertEqual(resposta["id"], "sintetico")
            self.assertEqual(resposta.cabecalhos["x-request-id"], "consulta")
            self.assertNotIn("set-cookie", resposta.cabecalhos)
            self.assertNotIn("mc_sintetica", repr(cliente))
            self.assertNotIn("sintetico", repr(resposta))
        self.assertEqual(len(chamadas), 1)

    def test_fornecedor_ausente_nao_herda_chave_global(self):
        chamadas = []
        with patch.dict(os.environ, {"MAILCORE_API_KEY": "mc_global_privilegiada"}):
            with Cliente(
                lambda: None,
                transporte_http=httpx.MockTransport(lambda pedido: chamadas.append(pedido)),
            ) as cliente:
                with self.assertRaises(ErroConfiguracao) as contexto:
                    cliente.emails.listar()
        self.assertEqual(chamadas, [])
        self.assertNotIn("mc_global", str(contexto.exception))

    def test_excecao_de_transporte_nao_reflete_url_ou_segredo(self):
        def falhar(pedido):
            raise httpx.ConnectError("mc_sintetica url_privada", request=pedido)

        with Cliente("mc_sintetica", transporte_http=httpx.MockTransport(falhar)) as cliente:
            with self.assertRaises(ErroTransporte) as contexto:
                cliente.emails.listar()
        self.assertNotIn("mc_sintetica", str(contexto.exception))
        self.assertNotIn("url_privada", str(contexto.exception))
        self.assertTrue(contexto.exception.__suppress_context__)

    def test_corpo_em_memoria_respeita_teto_e_fluxo_fecha_ao_sair(self):
        adaptador = httpx.MockTransport(
            lambda pedido: httpx.Response(200, content=b"original\x00\xff")
        )
        with Cliente("mc_sintetica", transporte_http=adaptador) as cliente:
            with self.assertRaises(ErroResposta):
                cliente.recebimento.baixar_original("id", limite_resposta_bytes=2)
            with cliente.recebimento.baixar_original_fluxo("id") as fluxo:
                self.assertEqual(b"".join(fluxo), b"original\x00\xff")
            with self.assertRaises(ErroConfiguracao):
                next(iter(fluxo))

    def test_dados_none_false_e_mapping_nao_sao_mutados(self):
        from types import MappingProxyType

        pedidos = []
        adaptador = httpx.MockTransport(
            lambda pedido: (
                pedidos.append(json.loads(pedido.content)) or httpx.Response(200, json={})
            )
        )
        dados = MappingProxyType({"nome": None, "ativo": False, "filhos": (1, 2)})
        with Cliente("mc_sintetica", transporte_http=adaptador) as cliente:
            cliente.contatos.criar(dados)
        self.assertEqual(pedidos, [{"nome": None, "ativo": False, "filhos": [1, 2]}])
        self.assertEqual(dados["filhos"], (1, 2))

    def test_resposta_inspecao_e_imutabilidade_de_metadados(self):
        resposta = Resposta({"segredo": "privado"}, 200, {"x-request-id": "id"})
        self.assertEqual(repr(resposta), "Resposta(status=200)")
        with self.assertRaises(TypeError):
            resposta.cabecalhos["outro"] = "valor"


class TestesAdaptadorAsync(unittest.IsolatedAsyncioTestCase):
    async def test_mock_convencional_e_fluxo_binario_async(self):
        adaptador = httpx.MockTransport(
            lambda pedido: httpx.Response(200, content=b"original\x00\xff")
        )
        async with ClienteAsync("mc_sintetica", transporte_http=adaptador) as cliente:
            self.assertEqual(
                (await cliente.recebimento.baixar_original("id")).dados, b"original\x00\xff"
            )
            async with cliente.recebimento.baixar_original_fluxo("id") as fluxo:
                self.assertEqual(b"".join([parte async for parte in fluxo]), b"original\x00\xff")
            with self.assertRaises(ErroConfiguracao):
                await anext(fluxo.__aiter__())

    async def test_fornecedor_ausente_async_falha_sem_chave_global(self):
        chamadas = []
        with patch.dict(os.environ, {"MAILCORE_API_KEY": "mc_global_privilegiada"}):
            async with ClienteAsync(
                lambda: None,
                transporte_http=httpx.MockTransport(lambda pedido: chamadas.append(pedido)),
            ) as cliente:
                with self.assertRaises(ErroConfiguracao):
                    await cliente.emails.listar()
        self.assertEqual(chamadas, [])


if __name__ == "__main__":
    unittest.main()
