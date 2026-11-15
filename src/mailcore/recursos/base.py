"""Base fina: um método do recurso corresponde a uma operação HTTP."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Unpack
from urllib.parse import quote

from ..erros import ErroConfiguracao
from ..tipos import GestorFluxo, GestorFluxoAsync, OpcoesRequisicao, Resposta

if TYPE_CHECKING:
    from ..transporte import Transporte, TransporteAsync


def segmento(valor: str) -> str:
    if (
        not isinstance(valor, str)
        or not valor
        or valor in {".", ".."}
        or re.search(r"[\x00-\x1f\x7f]", valor)
    ):
        raise ErroConfiguracao("Informe um identificador não vazio e sem controles.")
    try:
        return quote(valor, safe="-._~")
    except UnicodeError:
        raise ErroConfiguracao("O identificador deve ser UTF-8 válido.") from None


class RecursoBase:
    def __init__(self, transporte: Transporte) -> None:
        self._transporte = transporte

    def _executar(self, metodo: str, caminho: str, **opcoes: Any) -> Resposta[Any]:
        return self._transporte.executar(metodo, caminho, **opcoes)

    def _fluxo(self, metodo: str, caminho: str, **opcoes: Unpack[OpcoesRequisicao]) -> GestorFluxo:
        return self._transporte.fluxo(metodo, caminho, formato="fluxo", **opcoes)


class RecursoBaseAsync:
    def __init__(self, transporte: TransporteAsync) -> None:
        self._transporte = transporte

    async def _executar(self, metodo: str, caminho: str, **opcoes: Any) -> Resposta[Any]:
        return await self._transporte.executar(metodo, caminho, **opcoes)

    def _fluxo(
        self, metodo: str, caminho: str, **opcoes: Unpack[OpcoesRequisicao]
    ) -> GestorFluxoAsync:
        return self._transporte.fluxo(metodo, caminho, formato="fluxo", **opcoes)
