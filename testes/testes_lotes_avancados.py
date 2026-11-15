"""Composição em lotes/modelos mantém o JSON público, sem HTTP externo."""

import json
import unittest

import httpx

from mailcore import Cliente, ClienteAsync, PedidoEmailLote


def lote() -> list[PedidoEmailLote]:
    return [
        {
            "remetente": "origem@example.test",
            "destinatarios": ["pessoa@example.test"],
            "assunto": "Básico",
            "texto": "Primeiro",
        },
        {
            "remetente": "Equipe São Paulo <origem@example.test>",
            "destinatarios": ["para@example.test"],
            "cc": ["copia@example.test"],
            "cco": ["oculto@example.test"],
            "cabecalhos": {"X-Referencia": 'ação "especial"'},
            "assunto": "Composto",
            "html": "<p>Segundo</p>",
            "anexos": [],
            "tags": {"origem": "lote-avançado"},
        },
        {
            "modelo": {"id": "boas-vindas", "variaveis": {"NOME": "Ana", "TOTAL": 0}},
            "remetente": "Equipe São Paulo <origem@example.test>",
            "destinatarios": [],
            "cc": ["copia@example.test"],
            "cco": ["oculto@example.test"],
            "cabecalhos": {"X-Referencia": "modelo"},
        },
    ]


class TestesLotesAvancados(unittest.TestCase):
    def test_lote_misto_preserva_ordem_composicao_e_idempotencia_sem_repeticao(self):
        pedidos = []
        dados = lote()
        esperado = {"dados": [{"id": str(i), "estado": "aceita"} for i in range(3)]}

        def responder(pedido):
            pedidos.append(pedido)
            return httpx.Response(202, json=esperado)

        with Cliente("mc_sintetica", transporte_http=httpx.MockTransport(responder)) as cliente:
            resposta = cliente.lotes.enviar(dados, chave_idempotencia="intencao-lote")
        self.assertEqual(resposta.dados, esperado)
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(pedidos[0].url.path, "/v1/emails/batch")
        self.assertEqual(pedidos[0].headers["idempotency-key"], "intencao-lote")
        self.assertNotIn("X-Referencia", pedidos[0].headers)
        self.assertEqual(json.loads(pedidos[0].content), dados)

    def test_modelo_individual_preserva_composicao_e_anexo_comum(self):
        pedidos = []

        def responder(pedido):
            pedidos.append(pedido)
            return httpx.Response(202, json={"id": "modelo", "estado": "aceita"})

        dados = {
            "modelo": {"id": "modelo-publicado"},
            "remetente": "Equipe São Paulo <origem@example.test>",
            "destinatarios": [],
            "cc": ["copia@example.test"],
            "cco": ["oculto@example.test"],
            "cabecalhos": {"X-Referencia": "modelo"},
            "anexos": [
                {"nome": "recibo.txt", "tipo_conteudo": "text/plain", "conteudo_base64": "QQ=="}
            ],
        }
        with Cliente("mc_sintetica", transporte_http=httpx.MockTransport(responder)) as cliente:
            cliente.emails.enviar(dados)
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(json.loads(pedidos[0].content), dados)


class TestesLotesAvancadosAsync(unittest.IsolatedAsyncioTestCase):
    async def test_lote_async_preserva_mesmo_contrato(self):
        pedidos = []
        dados = lote()

        def responder(pedido):
            pedidos.append(pedido)
            return httpx.Response(202, json={"dados": [{"id": "async", "estado": "aceita"}]})

        async with ClienteAsync(
            "mc_sintetica", transporte_http=httpx.MockTransport(responder)
        ) as cliente:
            await cliente.lotes.enviar(dados, chave_idempotencia="lote-async")
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(pedidos[0].headers["idempotency-key"], "lote-async")
        self.assertEqual(json.loads(pedidos[0].content), dados)
