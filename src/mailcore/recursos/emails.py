"""Operações de emails do contrato público Mailcore."""

from __future__ import annotations

# Fonte estática; manutenção em scripts/gerar_recursos.py.
from collections.abc import Mapping, Sequence
from typing import Any, Unpack

from ..erros import ErroConfiguracao
from ..tipos import (
    OpcoesRequisicao,
    PedidoEmail,
    PedidoEmailLote,
    Resposta,
    RespostaEnvio,
    RespostaLote,
)
from .base import RecursoBase, RecursoBaseAsync, segmento


class Emails(RecursoBase):
    def enviar(
        self,
        dados: PedidoEmail,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[RespostaEnvio]:
        """Aceita a intenção de envio; a entrega é acompanhada separadamente."""
        return self._executar(
            "POST",
            "/emails",
            corpo=dados,
            **opcoes,
        )

    def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            "/emails",
            consulta=filtros,
            **opcoes,
        )

    def obter(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/emails/{segmento(id)}",
            **opcoes,
        )

    def reagendar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "PATCH",
            f"/emails/{segmento(id)}",
            corpo=pedido,
            **opcoes,
        )

    def cancelar(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/emails/{segmento(id)}/cancel",
            **opcoes,
        )

    def obter_por_idempotencia(
        self,
        chave: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/emails/idempotency/{segmento(chave)}",
            **opcoes,
        )

    def eventos(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/emails/{segmento(id)}/events",
            **opcoes,
        )

    def baixar_anexo(
        self,
        id: str,
        indice: int,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[bytes]:
        if isinstance(indice, bool) or not isinstance(indice, int) or indice < 0:
            raise ErroConfiguracao("Informe um índice de anexo inteiro e não negativo.")
        return self._executar(
            "GET",
            f"/emails/{segmento(id)}/attachments/{indice}",
            formato="bytes",
            **opcoes,
        )


class Lotes(RecursoBase):
    def enviar(
        self,
        dados: Sequence[PedidoEmailLote],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[RespostaLote]:
        return self._executar(
            "POST",
            "/emails/batch",
            corpo=list(dados),
            **opcoes,
        )

    def obter_por_idempotencia(
        self,
        chave: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/emails/batch/idempotency/{segmento(chave)}",
            **opcoes,
        )


class EmailsAsync(RecursoBaseAsync):
    async def enviar(
        self,
        dados: PedidoEmail,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[RespostaEnvio]:
        """Aceita a intenção de envio; a entrega é acompanhada separadamente."""
        return await self._executar(
            "POST",
            "/emails",
            corpo=dados,
            **opcoes,
        )

    async def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            "/emails",
            consulta=filtros,
            **opcoes,
        )

    async def obter(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/emails/{segmento(id)}",
            **opcoes,
        )

    async def reagendar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "PATCH",
            f"/emails/{segmento(id)}",
            corpo=pedido,
            **opcoes,
        )

    async def cancelar(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/emails/{segmento(id)}/cancel",
            **opcoes,
        )

    async def obter_por_idempotencia(
        self,
        chave: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/emails/idempotency/{segmento(chave)}",
            **opcoes,
        )

    async def eventos(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/emails/{segmento(id)}/events",
            **opcoes,
        )

    async def baixar_anexo(
        self,
        id: str,
        indice: int,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[bytes]:
        if isinstance(indice, bool) or not isinstance(indice, int) or indice < 0:
            raise ErroConfiguracao("Informe um índice de anexo inteiro e não negativo.")
        return await self._executar(
            "GET",
            f"/emails/{segmento(id)}/attachments/{indice}",
            formato="bytes",
            **opcoes,
        )


class LotesAsync(RecursoBaseAsync):
    async def enviar(
        self,
        dados: Sequence[PedidoEmailLote],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[RespostaLote]:
        return await self._executar(
            "POST",
            "/emails/batch",
            corpo=list(dados),
            **opcoes,
        )

    async def obter_por_idempotencia(
        self,
        chave: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/emails/batch/idempotency/{segmento(chave)}",
            **opcoes,
        )
