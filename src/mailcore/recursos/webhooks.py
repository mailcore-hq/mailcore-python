"""Operações de webhooks do contrato público Mailcore."""

from __future__ import annotations

# Fonte estática; manutenção em scripts/gerar_recursos.py.
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Unpack

from ..tipos import (
    OpcoesRequisicao,
    Resposta,
)
from .base import RecursoBase, RecursoBaseAsync, segmento

if TYPE_CHECKING:
    from ..transporte import Transporte, TransporteAsync


class EventosWebhook(RecursoBase):
    def listar(
        self,
        webhook_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/webhooks/{segmento(webhook_id)}/events",
            consulta=filtros,
            **opcoes,
        )

    def obter(
        self,
        webhook_id: str,
        evento_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/webhooks/{segmento(webhook_id)}/events/{segmento(evento_id)}",
            **opcoes,
        )

    def listar_tentativas(
        self,
        webhook_id: str,
        evento_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/webhooks/{segmento(webhook_id)}/events/{segmento(evento_id)}/attempts",
            consulta=filtros,
            **opcoes,
        )

    def reenviar(
        self,
        webhook_id: str,
        evento_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/webhooks/{segmento(webhook_id)}/events/{segmento(evento_id)}/replay",
            **opcoes,
        )


class Webhooks(RecursoBase):
    def __init__(self, transporte: Transporte) -> None:
        super().__init__(transporte)
        self.eventos: EventosWebhook = EventosWebhook(transporte)

    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/webhooks",
            corpo=pedido,
            **opcoes,
        )

    def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            "/webhooks",
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
            f"/webhooks/{segmento(id)}",
            **opcoes,
        )

    def atualizar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "PATCH",
            f"/webhooks/{segmento(id)}",
            corpo=pedido,
            **opcoes,
        )

    def remover(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "DELETE",
            f"/webhooks/{segmento(id)}",
            **opcoes,
        )


class EventosWebhookAsync(RecursoBaseAsync):
    async def listar(
        self,
        webhook_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/webhooks/{segmento(webhook_id)}/events",
            consulta=filtros,
            **opcoes,
        )

    async def obter(
        self,
        webhook_id: str,
        evento_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/webhooks/{segmento(webhook_id)}/events/{segmento(evento_id)}",
            **opcoes,
        )

    async def listar_tentativas(
        self,
        webhook_id: str,
        evento_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/webhooks/{segmento(webhook_id)}/events/{segmento(evento_id)}/attempts",
            consulta=filtros,
            **opcoes,
        )

    async def reenviar(
        self,
        webhook_id: str,
        evento_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/webhooks/{segmento(webhook_id)}/events/{segmento(evento_id)}/replay",
            **opcoes,
        )


class WebhooksAsync(RecursoBaseAsync):
    def __init__(self, transporte: TransporteAsync) -> None:
        super().__init__(transporte)
        self.eventos: EventosWebhookAsync = EventosWebhookAsync(transporte)

    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/webhooks",
            corpo=pedido,
            **opcoes,
        )

    async def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            "/webhooks",
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
            f"/webhooks/{segmento(id)}",
            **opcoes,
        )

    async def atualizar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "PATCH",
            f"/webhooks/{segmento(id)}",
            corpo=pedido,
            **opcoes,
        )

    async def remover(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "DELETE",
            f"/webhooks/{segmento(id)}",
            **opcoes,
        )
