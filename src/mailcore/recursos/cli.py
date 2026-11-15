"""Operações de cli do contrato público Mailcore."""

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


class ConcessoesCli(RecursoBase):
    def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            "/cli/oauth/grants",
            consulta=filtros,
            **opcoes,
        )

    def revogar(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/cli/oauth/grants/{segmento(id)}/revoke",
            **opcoes,
        )


class CliMailcore(RecursoBase):
    def __init__(self, transporte: Transporte) -> None:
        super().__init__(transporte)
        self.concessoes: ConcessoesCli = ConcessoesCli(transporte)


class ConcessoesCliAsync(RecursoBaseAsync):
    async def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            "/cli/oauth/grants",
            consulta=filtros,
            **opcoes,
        )

    async def revogar(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/cli/oauth/grants/{segmento(id)}/revoke",
            **opcoes,
        )


class CliMailcoreAsync(RecursoBaseAsync):
    def __init__(self, transporte: TransporteAsync) -> None:
        super().__init__(transporte)
        self.concessoes: ConcessoesCliAsync = ConcessoesCliAsync(transporte)
