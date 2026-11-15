"""Operações de contatos do contrato público Mailcore."""

from __future__ import annotations

# Fonte estática; manutenção em scripts/gerar_recursos.py.
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Unpack

from ..tipos import (
    GestorFluxo,
    GestorFluxoAsync,
    OpcoesRequisicao,
    Resposta,
)
from .base import RecursoBase, RecursoBaseAsync, segmento

if TYPE_CHECKING:
    from ..transporte import Transporte, TransporteAsync


class SegmentosContato(RecursoBase):
    def listar(
        self,
        contato_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/contacts/{segmento(contato_id)}/segments",
            **opcoes,
        )

    def adicionar(
        self,
        contato_id: str,
        segmento_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/contacts/{segmento(contato_id)}/segments",
            corpo={"segmento_id": segmento_id},
            aceitar_vazio=True,
            **opcoes,
        )

    def remover(
        self,
        contato_id: str,
        segmento_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "DELETE",
            f"/contacts/{segmento(contato_id)}/segments/{segmento(segmento_id)}",
            **opcoes,
        )


class TopicosContato(RecursoBase):
    def listar(
        self,
        contato_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/contacts/{segmento(contato_id)}/topics",
            **opcoes,
        )

    def atualizar(
        self,
        contato_id: str,
        topicos: list[Mapping[str, Any]],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "PATCH",
            f"/contacts/{segmento(contato_id)}/topics",
            corpo={"topicos": topicos},
            **opcoes,
        )


class ImportacoesContatos(RecursoBase):
    def prever(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/contacts/imports/preview",
            corpo=pedido,
            **opcoes,
        )

    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/contacts/imports",
            corpo=pedido,
            **opcoes,
        )

    def obter(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/contacts/imports/{segmento(id)}",
            **opcoes,
        )


class ExportacoesContatos(RecursoBase):
    def criar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/contacts/exports",
            corpo={} if filtros is None else filtros,
            **opcoes,
        )

    def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            "/contacts/exports",
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
            f"/contacts/exports/{segmento(id)}",
            **opcoes,
        )

    def baixar(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[bytes]:
        return self._executar(
            "GET",
            f"/contacts/exports/{segmento(id)}/download",
            formato="bytes",
            **opcoes,
        )

    def baixar_fluxo(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> GestorFluxo:
        return self._fluxo(
            "GET",
            f"/contacts/exports/{segmento(id)}/download",
            **opcoes,
        )


class Contatos(RecursoBase):
    def __init__(self, transporte: Transporte) -> None:
        super().__init__(transporte)
        self.segmentos: SegmentosContato = SegmentosContato(transporte)
        self.topicos: TopicosContato = TopicosContato(transporte)
        self.importacoes: ImportacoesContatos = ImportacoesContatos(transporte)
        self.exportacoes: ExportacoesContatos = ExportacoesContatos(transporte)

    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/contacts",
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
            "/contacts",
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
            f"/contacts/{segmento(id)}",
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
            f"/contacts/{segmento(id)}",
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
            f"/contacts/{segmento(id)}",
            **opcoes,
        )

    def adicionar_em_lote(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/contacts/batch",
            corpo=pedido,
            **opcoes,
        )

    def alterar_em_lote(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/contacts/bulk",
            corpo=pedido,
            **opcoes,
        )


class Segmentos(RecursoBase):
    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/segments",
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
            "/segments",
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
            f"/segments/{segmento(id)}",
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
            f"/segments/{segmento(id)}",
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
            f"/segments/{segmento(id)}",
            **opcoes,
        )


class Topicos(RecursoBase):
    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/topics",
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
            "/topics",
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
            f"/topics/{segmento(id)}",
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
            f"/topics/{segmento(id)}",
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
            f"/topics/{segmento(id)}",
            **opcoes,
        )


class PropriedadesContatos(RecursoBase):
    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/contact-properties",
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
            "/contact-properties",
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
            f"/contact-properties/{segmento(id)}",
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
            f"/contact-properties/{segmento(id)}",
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
            f"/contact-properties/{segmento(id)}",
            **opcoes,
        )


class SegmentosContatoAsync(RecursoBaseAsync):
    async def listar(
        self,
        contato_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/contacts/{segmento(contato_id)}/segments",
            **opcoes,
        )

    async def adicionar(
        self,
        contato_id: str,
        segmento_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/contacts/{segmento(contato_id)}/segments",
            corpo={"segmento_id": segmento_id},
            aceitar_vazio=True,
            **opcoes,
        )

    async def remover(
        self,
        contato_id: str,
        segmento_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "DELETE",
            f"/contacts/{segmento(contato_id)}/segments/{segmento(segmento_id)}",
            **opcoes,
        )


class TopicosContatoAsync(RecursoBaseAsync):
    async def listar(
        self,
        contato_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/contacts/{segmento(contato_id)}/topics",
            **opcoes,
        )

    async def atualizar(
        self,
        contato_id: str,
        topicos: list[Mapping[str, Any]],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "PATCH",
            f"/contacts/{segmento(contato_id)}/topics",
            corpo={"topicos": topicos},
            **opcoes,
        )


class ImportacoesContatosAsync(RecursoBaseAsync):
    async def prever(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/contacts/imports/preview",
            corpo=pedido,
            **opcoes,
        )

    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/contacts/imports",
            corpo=pedido,
            **opcoes,
        )

    async def obter(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/contacts/imports/{segmento(id)}",
            **opcoes,
        )


class ExportacoesContatosAsync(RecursoBaseAsync):
    async def criar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/contacts/exports",
            corpo={} if filtros is None else filtros,
            **opcoes,
        )

    async def listar(
        self,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            "/contacts/exports",
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
            f"/contacts/exports/{segmento(id)}",
            **opcoes,
        )

    async def baixar(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[bytes]:
        return await self._executar(
            "GET",
            f"/contacts/exports/{segmento(id)}/download",
            formato="bytes",
            **opcoes,
        )

    def baixar_fluxo(
        self,
        id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> GestorFluxoAsync:
        return self._fluxo(
            "GET",
            f"/contacts/exports/{segmento(id)}/download",
            **opcoes,
        )


class ContatosAsync(RecursoBaseAsync):
    def __init__(self, transporte: TransporteAsync) -> None:
        super().__init__(transporte)
        self.segmentos: SegmentosContatoAsync = SegmentosContatoAsync(transporte)
        self.topicos: TopicosContatoAsync = TopicosContatoAsync(transporte)
        self.importacoes: ImportacoesContatosAsync = ImportacoesContatosAsync(transporte)
        self.exportacoes: ExportacoesContatosAsync = ExportacoesContatosAsync(transporte)

    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/contacts",
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
            "/contacts",
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
            f"/contacts/{segmento(id)}",
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
            f"/contacts/{segmento(id)}",
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
            f"/contacts/{segmento(id)}",
            **opcoes,
        )

    async def adicionar_em_lote(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/contacts/batch",
            corpo=pedido,
            **opcoes,
        )

    async def alterar_em_lote(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/contacts/bulk",
            corpo=pedido,
            **opcoes,
        )


class SegmentosAsync(RecursoBaseAsync):
    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/segments",
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
            "/segments",
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
            f"/segments/{segmento(id)}",
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
            f"/segments/{segmento(id)}",
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
            f"/segments/{segmento(id)}",
            **opcoes,
        )


class TopicosAsync(RecursoBaseAsync):
    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/topics",
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
            "/topics",
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
            f"/topics/{segmento(id)}",
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
            f"/topics/{segmento(id)}",
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
            f"/topics/{segmento(id)}",
            **opcoes,
        )


class PropriedadesContatosAsync(RecursoBaseAsync):
    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/contact-properties",
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
            "/contact-properties",
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
            f"/contact-properties/{segmento(id)}",
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
            f"/contact-properties/{segmento(id)}",
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
            f"/contact-properties/{segmento(id)}",
            **opcoes,
        )
