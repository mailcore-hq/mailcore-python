"""Exemplos de consumidor conferidos pelo mypy, sem executar HTTP."""

from typing import assert_type

from mailcore import (
    AnexoEmail,
    Cliente,
    ClienteAsync,
    EmailComModelo,
    PedidoEmail,
    PedidoEmailLote,
    Resposta,
    RespostaEnvio,
    RespostaLote,
)
from mailcore.tipos import EmailModeloLote, EmailTextoLote

PEDIDO: PedidoEmail = {
    "remetente": "equipe@example.test",
    "destinatarios": ["pessoa@example.test"],
    "assunto": "Confirmação",
    "html": "<p>Confirmado</p>",
}
LOTE: PedidoEmailLote = {
    "remetente": "equipe@example.test",
    "destinatarios": ["pessoa@example.test"],
    "assunto": "Confirmação",
    "texto": "Confirmado",
    "cc": ["copia@example.test"],
    "cco": ["oculto@example.test"],
    "cabecalhos": {"X-Referencia": "confirmacao"},
    "anexos": [],
}
LOTE_MODELO: PedidoEmailLote = {
    "modelo": {"id": "boas-vindas", "variaveis": {"NOME": "Ana"}},
    "remetente": "Equipe São Paulo <origem@example.test>",
    "destinatarios": [],
    "cc": ["copia@example.test"],
    "cco": ["oculto@example.test"],
    "cabecalhos": {"X-Referencia": "modelo"},
    "anexos": [],
}


def consumir(cliente: Cliente) -> None:
    assert_type(cliente.emails.enviar(PEDIDO), Resposta[RespostaEnvio])
    assert_type(cliente.lotes.enviar([LOTE, LOTE_MODELO]), Resposta[RespostaLote])
    assert_type(cliente.recebimento.baixar_original("id"), Resposta[bytes])
    with cliente.recebimento.baixar_original_fluxo("id") as fluxo:
        for parte in fluxo:
            assert_type(parte, bytes)


async def consumir_async(cliente: ClienteAsync) -> None:
    assert_type(await cliente.emails.enviar(PEDIDO), Resposta[RespostaEnvio])
    assert_type(await cliente.lotes.enviar([LOTE, LOTE_MODELO]), Resposta[RespostaLote])
    assert_type(await cliente.recebimento.baixar_original("id"), Resposta[bytes])
    async with cliente.recebimento.baixar_original_fluxo("id") as fluxo:
        async for parte in fluxo:
            assert_type(parte, bytes)


# O verificador exige esse diagnóstico; remover a proteção gera unused-ignore.
MODELO_INVALIDO: EmailComModelo = {
    "destinatarios": ["pessoa@example.test"],
    "modelo": {"id": "id"},
    "html": "incompatível",  # type: ignore[typeddict-unknown-key]
}

ANEXO_COMUM: AnexoEmail = {
    "nome": "recibo.txt",
    "tipo_conteudo": "text/plain",
    "conteudo_base64": "QQ==",
}
LOTE_ANEXO_INVALIDO: EmailTextoLote = {
    "remetente": "origem@example.test",
    "destinatarios": ["p@example.test"],
    "assunto": "Teste",
    "texto": "Um",
    "anexos": [ANEXO_COMUM],  # type: ignore[list-item]
}
MODELO_LOTE_CORPO_INVALIDO: EmailModeloLote = {
    "modelo": {"id": "modelo"},
    "destinatarios": ["p@example.test"],
    "texto": None,  # type: ignore[typeddict-unknown-key]
}
MODELO_CID_INVALIDO: EmailComModelo = {
    "modelo": {"id": "modelo"},
    "destinatarios": ["p@example.test"],
    "anexos": [
        {
            "nome": "logo.png",
            "tipo_conteudo": "image/png",
            "conteudo_base64": "QQ==",
            "id_conteudo": "logo",  # type: ignore[typeddict-unknown-key]
        }
    ],
}
