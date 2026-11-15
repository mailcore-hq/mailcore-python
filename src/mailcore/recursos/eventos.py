"""Operações de eventos do contrato público Mailcore."""

from __future__ import annotations

# Fonte estática; manutenção em scripts/gerar_recursos.py.
from collections.abc import Mapping
from typing import Any, Unpack

from ..tipos import (
    OpcoesRequisicao,
    Resposta,
)
from .base import RecursoBase, RecursoBaseAsync, segmento


class Eventos(RecursoBase):
    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/events",
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
            "/events",
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
            f"/events/{segmento(id)}",
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
            f"/events/{segmento(id)}",
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
            f"/events/{segmento(id)}",
            **opcoes,
        )

    def enviar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/events/send",
            corpo=pedido,
            **opcoes,
        )


class EventosAsync(RecursoBaseAsync):
    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/events",
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
            "/events",
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
            f"/events/{segmento(id)}",
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
            f"/events/{segmento(id)}",
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
            f"/events/{segmento(id)}",
            **opcoes,
        )

    async def enviar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/events/send",
            corpo=pedido,
            **opcoes,
        )
