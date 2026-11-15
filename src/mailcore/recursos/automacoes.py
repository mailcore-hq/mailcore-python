"""Operações de automacoes do contrato público Mailcore."""

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


class ExecucoesAutomacoes(RecursoBase):
    def listar(
        self,
        automacao_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/automations/{segmento(automacao_id)}/runs",
            consulta=filtros,
            **opcoes,
        )

    def obter(
        self,
        automacao_id: str,
        execucao_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/automations/{segmento(automacao_id)}/runs/{segmento(execucao_id)}",
            **opcoes,
        )


class Automacoes(RecursoBase):
    def __init__(self, transporte: Transporte) -> None:
        super().__init__(transporte)
        self.execucoes: ExecucoesAutomacoes = ExecucoesAutomacoes(transporte)

    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/automations",
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
            "/automations",
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
            f"/automations/{segmento(id)}",
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
            f"/automations/{segmento(id)}",
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
            f"/automations/{segmento(id)}",
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
            f"/automations/{segmento(id)}/duplicate",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )

    def parar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/automations/{segmento(id)}/stop",
            corpo=pedido,
            **opcoes,
        )


class ExecucoesAutomacoesAsync(RecursoBaseAsync):
    async def listar(
        self,
        automacao_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/automations/{segmento(automacao_id)}/runs",
            consulta=filtros,
            **opcoes,
        )

    async def obter(
        self,
        automacao_id: str,
        execucao_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/automations/{segmento(automacao_id)}/runs/{segmento(execucao_id)}",
            **opcoes,
        )


class AutomacoesAsync(RecursoBaseAsync):
    def __init__(self, transporte: TransporteAsync) -> None:
        super().__init__(transporte)
        self.execucoes: ExecucoesAutomacoesAsync = ExecucoesAutomacoesAsync(transporte)

    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/automations",
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
            "/automations",
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
            f"/automations/{segmento(id)}",
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
            f"/automations/{segmento(id)}",
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
            f"/automations/{segmento(id)}",
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
            f"/automations/{segmento(id)}/duplicate",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )

    async def parar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/automations/{segmento(id)}/stop",
            corpo=pedido,
            **opcoes,
        )
