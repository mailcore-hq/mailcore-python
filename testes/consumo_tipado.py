"""Exemplos de consumidor conferidos pelo mypy, sem executar HTTP."""

from typing import assert_type

from mailcore import (
    Cliente,
    ClienteAsync,
    EmailComModelo,
    PedidoEmail,
    PedidoEmailLote,
    Resposta,
    RespostaEnvio,
    RespostaLote,
)

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
}


def consumir(cliente: Cliente) -> None:
    assert_type(cliente.emails.enviar(PEDIDO), Resposta[RespostaEnvio])
    assert_type(cliente.lotes.enviar([LOTE]), Resposta[RespostaLote])
    assert_type(cliente.recebimento.baixar_original("id"), Resposta[bytes])
    with cliente.recebimento.baixar_original_fluxo("id") as fluxo:
        for parte in fluxo:
            assert_type(parte, bytes)


async def consumir_async(cliente: ClienteAsync) -> None:
    assert_type(await cliente.emails.enviar(PEDIDO), Resposta[RespostaEnvio])
    assert_type(await cliente.lotes.enviar([LOTE]), Resposta[RespostaLote])
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
