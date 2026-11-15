"""Operações de campanhas do contrato público Mailcore."""

from __future__ import annotations

# Fonte estática; manutenção em scripts/gerar_recursos.py.
from collections.abc import Mapping
from typing import Any, Unpack

from ..tipos import (
    OpcoesRequisicao,
    Resposta,
)
from .base import RecursoBase, RecursoBaseAsync, segmento


class Campanhas(RecursoBase):
    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/broadcasts",
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
            "/broadcasts",
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
            f"/broadcasts/{segmento(id)}",
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
            f"/broadcasts/{segmento(id)}",
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
            f"/broadcasts/{segmento(id)}",
            **opcoes,
        )

    def duplicar(
        self,
        id: str,
        pedido: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/duplicate",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )

    def revisar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/review",
            corpo=pedido,
            **opcoes,
        )

    def enviar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/send",
            corpo=pedido,
            **opcoes,
        )

    def cancelar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/cancel",
            corpo=pedido,
            **opcoes,
        )

    def prever(
        self,
        id: str,
        pedido: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/preview",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )

    def testar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/test",
            corpo=pedido,
            **opcoes,
        )

    def ler_previa(
        self,
        organizacao_id: str,
        previa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[str]:
        return self._executar(
            "GET",
            f"/broadcast-previews/{segmento(organizacao_id)}/{segmento(previa_id)}",
            formato="texto",
            **opcoes,
        )

    def obter_metricas(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/broadcasts/{segmento(id)}/metrics",
            **opcoes,
        )

    def listar_destinatarios(
        self,
        id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/broadcasts/{segmento(id)}/recipients",
            consulta=filtros,
            **opcoes,
        )

    def listar_links_clicados(
        self,
        id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/broadcasts/{segmento(id)}/clicked-links",
            consulta=filtros,
            **opcoes,
        )


class CampanhasAsync(RecursoBaseAsync):
    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/broadcasts",
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
            "/broadcasts",
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
            f"/broadcasts/{segmento(id)}",
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
            f"/broadcasts/{segmento(id)}",
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
            f"/broadcasts/{segmento(id)}",
            **opcoes,
        )

    async def duplicar(
        self,
        id: str,
        pedido: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/duplicate",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )

    async def revisar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/review",
            corpo=pedido,
            **opcoes,
        )

    async def enviar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/send",
            corpo=pedido,
            **opcoes,
        )

    async def cancelar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/cancel",
            corpo=pedido,
            **opcoes,
        )

    async def prever(
        self,
        id: str,
        pedido: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/preview",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )

    async def testar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/broadcasts/{segmento(id)}/test",
            corpo=pedido,
            **opcoes,
        )

    async def ler_previa(
        self,
        organizacao_id: str,
        previa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[str]:
        return await self._executar(
            "GET",
            f"/broadcast-previews/{segmento(organizacao_id)}/{segmento(previa_id)}",
            formato="texto",
            **opcoes,
        )

    async def obter_metricas(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/broadcasts/{segmento(id)}/metrics",
            **opcoes,
        )

    async def listar_destinatarios(
        self,
        id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/broadcasts/{segmento(id)}/recipients",
            consulta=filtros,
            **opcoes,
        )

    async def listar_links_clicados(
        self,
        id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/broadcasts/{segmento(id)}/clicked-links",
            consulta=filtros,
            **opcoes,
        )
