"""Operações de chaves api do contrato público Mailcore."""

from __future__ import annotations

# Fonte estática; manutenção em scripts/gerar_recursos.py.
from collections.abc import Mapping
from typing import Any, Unpack

from ..tipos import (
    OpcoesRequisicao,
    Resposta,
)
from .base import RecursoBase, RecursoBaseAsync, segmento


class ChavesApi(RecursoBase):
    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/api-keys",
            corpo=pedido,
            **opcoes,
        )

    def listar(
        self,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            "/api-keys",
            **opcoes,
        )

    def renomear(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "PATCH",
            f"/api-keys/{segmento(id)}",
            corpo=pedido,
            **opcoes,
        )

    def revogar(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "DELETE",
            f"/api-keys/{segmento(id)}",
            **opcoes,
        )


class ChavesApiAsync(RecursoBaseAsync):
    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/api-keys",
            corpo=pedido,
            **opcoes,
        )

    async def listar(
        self,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            "/api-keys",
            **opcoes,
        )

    async def renomear(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "PATCH",
            f"/api-keys/{segmento(id)}",
            corpo=pedido,
            **opcoes,
        )

    async def revogar(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "DELETE",
            f"/api-keys/{segmento(id)}",
            **opcoes,
        )
