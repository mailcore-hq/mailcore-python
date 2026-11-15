"""Operações de modelos do contrato público Mailcore."""

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


class VersoesModelo(RecursoBase):
    def listar(
        self,
        modelo_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/templates/{segmento(modelo_id)}/versions",
            consulta=filtros,
            **opcoes,
        )

    def obter(
        self,
        modelo_id: str,
        versao_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/templates/{segmento(modelo_id)}/versions/{segmento(versao_id)}",
            **opcoes,
        )

    def restaurar(
        self,
        modelo_id: str,
        versao_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/templates/{segmento(modelo_id)}/versions/{segmento(versao_id)}/restore",
            corpo=pedido,
            **opcoes,
        )

    def prever(
        self,
        modelo_id: str,
        versao_id: str,
        pedido: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/templates/{segmento(modelo_id)}/versions/{segmento(versao_id)}/preview",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )


class PastasModelo(RecursoBase):
    def listar(
        self,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            "/template-folders",
            **opcoes,
        )

    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/template-folders",
            corpo=pedido,
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
            f"/template-folders/{segmento(id)}",
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
            f"/template-folders/{segmento(id)}",
            **opcoes,
        )


class Modelos(RecursoBase):
    def __init__(self, transporte: Transporte) -> None:
        super().__init__(transporte)
        self.versoes: VersoesModelo = VersoesModelo(transporte)
        self.pastas: PastasModelo = PastasModelo(transporte)

    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/templates",
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
            "/templates",
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
            f"/templates/{segmento(id)}",
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
            f"/templates/{segmento(id)}",
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
            f"/templates/{segmento(id)}",
            **opcoes,
        )

    def prever(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/templates/{segmento(id)}/preview",
            corpo=pedido,
            **opcoes,
        )

    def obter_previa(
        self,
        organizacao_id: str,
        previa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[str]:
        return self._executar(
            "GET",
            f"/template-previews/{segmento(organizacao_id)}/{segmento(previa_id)}",
            formato="texto",
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
            f"/templates/{segmento(id)}/test",
            corpo=pedido,
            **opcoes,
        )

    def publicar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/templates/{segmento(id)}/publish",
            corpo=pedido,
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
            f"/templates/{segmento(id)}/duplicate",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )


class VersoesModeloAsync(RecursoBaseAsync):
    async def listar(
        self,
        modelo_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/templates/{segmento(modelo_id)}/versions",
            consulta=filtros,
            **opcoes,
        )

    async def obter(
        self,
        modelo_id: str,
        versao_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/templates/{segmento(modelo_id)}/versions/{segmento(versao_id)}",
            **opcoes,
        )

    async def restaurar(
        self,
        modelo_id: str,
        versao_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/templates/{segmento(modelo_id)}/versions/{segmento(versao_id)}/restore",
            corpo=pedido,
            **opcoes,
        )

    async def prever(
        self,
        modelo_id: str,
        versao_id: str,
        pedido: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/templates/{segmento(modelo_id)}/versions/{segmento(versao_id)}/preview",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )


class PastasModeloAsync(RecursoBaseAsync):
    async def listar(
        self,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            "/template-folders",
            **opcoes,
        )

    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/template-folders",
            corpo=pedido,
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
            f"/template-folders/{segmento(id)}",
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
            f"/template-folders/{segmento(id)}",
            **opcoes,
        )


class ModelosAsync(RecursoBaseAsync):
    def __init__(self, transporte: TransporteAsync) -> None:
        super().__init__(transporte)
        self.versoes: VersoesModeloAsync = VersoesModeloAsync(transporte)
        self.pastas: PastasModeloAsync = PastasModeloAsync(transporte)

    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/templates",
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
            "/templates",
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
            f"/templates/{segmento(id)}",
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
            f"/templates/{segmento(id)}",
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
            f"/templates/{segmento(id)}",
            **opcoes,
        )

    async def prever(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/templates/{segmento(id)}/preview",
            corpo=pedido,
            **opcoes,
        )

    async def obter_previa(
        self,
        organizacao_id: str,
        previa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[str]:
        return await self._executar(
            "GET",
            f"/template-previews/{segmento(organizacao_id)}/{segmento(previa_id)}",
            formato="texto",
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
            f"/templates/{segmento(id)}/test",
            corpo=pedido,
            **opcoes,
        )

    async def publicar(
        self,
        id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/templates/{segmento(id)}/publish",
            corpo=pedido,
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
            f"/templates/{segmento(id)}/duplicate",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )
