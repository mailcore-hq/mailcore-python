"""Operações de recebimento do contrato público Mailcore."""

from __future__ import annotations

# Fonte estática; manutenção em scripts/gerar_recursos.py.
from collections.abc import Mapping
from typing import Any, Unpack

from ..tipos import (
    GestorFluxo,
    GestorFluxoAsync,
    OpcoesRequisicao,
    Resposta,
)
from .base import RecursoBase, RecursoBaseAsync, segmento


class Recebimento(RecursoBase):
    def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            "/receiving",
            consulta=filtros,
            **opcoes,
        )

    def obter(
        self,
        id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/receiving/{segmento(id)}",
            consulta=filtros,
            **opcoes,
        )

    def listar_anexos(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/receiving/{segmento(id)}/attachments",
            **opcoes,
        )

    def obter_anexo(
        self,
        id: str,
        anexo_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/receiving/{segmento(id)}/attachments/{segmento(anexo_id)}",
            **opcoes,
        )

    def baixar_original(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[bytes]:
        return self._executar(
            "GET",
            f"/receiving/{segmento(id)}/raw",
            formato="bytes",
            **opcoes,
        )

    def baixar_anexo(
        self,
        id: str,
        anexo_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[bytes]:
        return self._executar(
            "GET",
            f"/receiving/{segmento(id)}/attachments/{segmento(anexo_id)}/download",
            formato="bytes",
            **opcoes,
        )

    def baixar_original_fluxo(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> GestorFluxo:
        return self._fluxo(
            "GET",
            f"/receiving/{segmento(id)}/raw",
            **opcoes,
        )

    def baixar_anexo_fluxo(
        self,
        id: str,
        anexo_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> GestorFluxo:
        return self._fluxo(
            "GET",
            f"/receiving/{segmento(id)}/attachments/{segmento(anexo_id)}/download",
            **opcoes,
        )


class RecebimentoAsync(RecursoBaseAsync):
    async def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            "/receiving",
            consulta=filtros,
            **opcoes,
        )

    async def obter(
        self,
        id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/receiving/{segmento(id)}",
            consulta=filtros,
            **opcoes,
        )

    async def listar_anexos(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/receiving/{segmento(id)}/attachments",
            **opcoes,
        )

    async def obter_anexo(
        self,
        id: str,
        anexo_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/receiving/{segmento(id)}/attachments/{segmento(anexo_id)}",
            **opcoes,
        )

    async def baixar_original(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[bytes]:
        return await self._executar(
            "GET",
            f"/receiving/{segmento(id)}/raw",
            formato="bytes",
            **opcoes,
        )

    async def baixar_anexo(
        self,
        id: str,
        anexo_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[bytes]:
        return await self._executar(
            "GET",
            f"/receiving/{segmento(id)}/attachments/{segmento(anexo_id)}/download",
            formato="bytes",
            **opcoes,
        )

    def baixar_original_fluxo(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> GestorFluxoAsync:
        return self._fluxo(
            "GET",
            f"/receiving/{segmento(id)}/raw",
            **opcoes,
        )

    def baixar_anexo_fluxo(
        self,
        id: str,
        anexo_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> GestorFluxoAsync:
        return self._fluxo(
            "GET",
            f"/receiving/{segmento(id)}/attachments/{segmento(anexo_id)}/download",
            **opcoes,
        )
