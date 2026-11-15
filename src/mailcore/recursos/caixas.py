"""Operações de caixas do contrato público Mailcore."""

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


class EmailsCaixa(RecursoBase):
    def listar(
        self,
        caixa_id: str,
        conversa_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/emails",
            consulta=filtros,
            **opcoes,
        )

    def obter(
        self,
        caixa_id: str,
        conversa_id: str,
        email_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/emails/{segmento(email_id)}",
            **opcoes,
        )

    def responder(
        self,
        caixa_id: str,
        conversa_id: str,
        email_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/emails/{segmento(email_id)}/reply",
            corpo=pedido,
            **opcoes,
        )

    def encaminhar(
        self,
        caixa_id: str,
        conversa_id: str,
        email_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/emails/{segmento(email_id)}/forward",
            corpo=pedido,
            **opcoes,
        )


class EtiquetasConversaCaixa(RecursoBase):
    def adicionar(
        self,
        caixa_id: str,
        conversa_id: str,
        ids: list[str],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/labels",
            corpo={"ids": ids},
            **opcoes,
        )

    def substituir(
        self,
        caixa_id: str,
        conversa_id: str,
        ids: list[str],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "PUT",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/labels",
            corpo={"ids": ids},
            **opcoes,
        )

    def remover(
        self,
        caixa_id: str,
        conversa_id: str,
        etiqueta_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "DELETE",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/labels/{segmento(etiqueta_id)}",
            **opcoes,
        )


class ConversasCaixa(RecursoBase):
    def __init__(self, transporte: Transporte) -> None:
        super().__init__(transporte)
        self.emails: EmailsCaixa = EmailsCaixa(transporte)
        self.etiquetas: EtiquetasConversaCaixa = EtiquetasConversaCaixa(transporte)

    def listar(
        self,
        caixa_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads",
            consulta=filtros,
            **opcoes,
        )

    def buscar(
        self,
        caixa_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads/search",
            consulta=filtros,
            **opcoes,
        )

    def obter(
        self,
        caixa_id: str,
        conversa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}",
            **opcoes,
        )

    def atualizar(
        self,
        caixa_id: str,
        conversa_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "PATCH",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}",
            corpo=pedido,
            **opcoes,
        )

    def remover(
        self,
        caixa_id: str,
        conversa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "DELETE",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}",
            **opcoes,
        )


class EtiquetasCaixa(RecursoBase):
    def listar(
        self,
        caixa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/labels",
            **opcoes,
        )

    def obter(
        self,
        caixa_id: str,
        etiqueta_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/labels/{segmento(etiqueta_id)}",
            **opcoes,
        )

    def criar(
        self,
        caixa_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/labels",
            corpo=pedido,
            **opcoes,
        )

    def atualizar(
        self,
        caixa_id: str,
        etiqueta_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "PATCH",
            f"/inboxes/{segmento(caixa_id)}/labels/{segmento(etiqueta_id)}",
            corpo=pedido,
            **opcoes,
        )

    def remover(
        self,
        caixa_id: str,
        etiqueta_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "DELETE",
            f"/inboxes/{segmento(caixa_id)}/labels/{segmento(etiqueta_id)}",
            **opcoes,
        )


class RascunhosCaixa(RecursoBase):
    def listar(
        self,
        caixa_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/drafts",
            consulta=filtros,
            **opcoes,
        )

    def obter(
        self,
        caixa_id: str,
        rascunho_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/drafts/{segmento(rascunho_id)}",
            **opcoes,
        )

    def criar(
        self,
        caixa_id: str,
        pedido: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/drafts",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )

    def atualizar(
        self,
        caixa_id: str,
        rascunho_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "PATCH",
            f"/inboxes/{segmento(caixa_id)}/drafts/{segmento(rascunho_id)}",
            corpo=pedido,
            **opcoes,
        )

    def remover(
        self,
        caixa_id: str,
        rascunho_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "DELETE",
            f"/inboxes/{segmento(caixa_id)}/drafts/{segmento(rascunho_id)}",
            **opcoes,
        )

    def enviar(
        self,
        caixa_id: str,
        rascunho_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/drafts/{segmento(rascunho_id)}/send",
            corpo=pedido,
            **opcoes,
        )


class Caixas(RecursoBase):
    def __init__(self, transporte: Transporte) -> None:
        super().__init__(transporte)
        self.conversas: ConversasCaixa = ConversasCaixa(transporte)
        self.etiquetas: EtiquetasCaixa = EtiquetasCaixa(transporte)
        self.rascunhos: RascunhosCaixa = RascunhosCaixa(transporte)

    def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return self._executar(
            "POST",
            "/inboxes",
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
            "/inboxes",
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
            f"/inboxes/{segmento(id)}",
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
            f"/inboxes/{segmento(id)}",
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
            f"/inboxes/{segmento(id)}",
            **opcoes,
        )


class EmailsCaixaAsync(RecursoBaseAsync):
    async def listar(
        self,
        caixa_id: str,
        conversa_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/emails",
            consulta=filtros,
            **opcoes,
        )

    async def obter(
        self,
        caixa_id: str,
        conversa_id: str,
        email_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/emails/{segmento(email_id)}",
            **opcoes,
        )

    async def responder(
        self,
        caixa_id: str,
        conversa_id: str,
        email_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/emails/{segmento(email_id)}/reply",
            corpo=pedido,
            **opcoes,
        )

    async def encaminhar(
        self,
        caixa_id: str,
        conversa_id: str,
        email_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/emails/{segmento(email_id)}/forward",
            corpo=pedido,
            **opcoes,
        )


class EtiquetasConversaCaixaAsync(RecursoBaseAsync):
    async def adicionar(
        self,
        caixa_id: str,
        conversa_id: str,
        ids: list[str],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/labels",
            corpo={"ids": ids},
            **opcoes,
        )

    async def substituir(
        self,
        caixa_id: str,
        conversa_id: str,
        ids: list[str],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "PUT",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/labels",
            corpo={"ids": ids},
            **opcoes,
        )

    async def remover(
        self,
        caixa_id: str,
        conversa_id: str,
        etiqueta_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "DELETE",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}/labels/{segmento(etiqueta_id)}",
            **opcoes,
        )


class ConversasCaixaAsync(RecursoBaseAsync):
    def __init__(self, transporte: TransporteAsync) -> None:
        super().__init__(transporte)
        self.emails: EmailsCaixaAsync = EmailsCaixaAsync(transporte)
        self.etiquetas: EtiquetasConversaCaixaAsync = EtiquetasConversaCaixaAsync(transporte)

    async def listar(
        self,
        caixa_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads",
            consulta=filtros,
            **opcoes,
        )

    async def buscar(
        self,
        caixa_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads/search",
            consulta=filtros,
            **opcoes,
        )

    async def obter(
        self,
        caixa_id: str,
        conversa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}",
            **opcoes,
        )

    async def atualizar(
        self,
        caixa_id: str,
        conversa_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "PATCH",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}",
            corpo=pedido,
            **opcoes,
        )

    async def remover(
        self,
        caixa_id: str,
        conversa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "DELETE",
            f"/inboxes/{segmento(caixa_id)}/threads/{segmento(conversa_id)}",
            **opcoes,
        )


class EtiquetasCaixaAsync(RecursoBaseAsync):
    async def listar(
        self,
        caixa_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/labels",
            **opcoes,
        )

    async def obter(
        self,
        caixa_id: str,
        etiqueta_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/labels/{segmento(etiqueta_id)}",
            **opcoes,
        )

    async def criar(
        self,
        caixa_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/labels",
            corpo=pedido,
            **opcoes,
        )

    async def atualizar(
        self,
        caixa_id: str,
        etiqueta_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "PATCH",
            f"/inboxes/{segmento(caixa_id)}/labels/{segmento(etiqueta_id)}",
            corpo=pedido,
            **opcoes,
        )

    async def remover(
        self,
        caixa_id: str,
        etiqueta_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "DELETE",
            f"/inboxes/{segmento(caixa_id)}/labels/{segmento(etiqueta_id)}",
            **opcoes,
        )


class RascunhosCaixaAsync(RecursoBaseAsync):
    async def listar(
        self,
        caixa_id: str,
        filtros: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/drafts",
            consulta=filtros,
            **opcoes,
        )

    async def obter(
        self,
        caixa_id: str,
        rascunho_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "GET",
            f"/inboxes/{segmento(caixa_id)}/drafts/{segmento(rascunho_id)}",
            **opcoes,
        )

    async def criar(
        self,
        caixa_id: str,
        pedido: Mapping[str, Any] | None = None,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/drafts",
            corpo={} if pedido is None else pedido,
            **opcoes,
        )

    async def atualizar(
        self,
        caixa_id: str,
        rascunho_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "PATCH",
            f"/inboxes/{segmento(caixa_id)}/drafts/{segmento(rascunho_id)}",
            corpo=pedido,
            **opcoes,
        )

    async def remover(
        self,
        caixa_id: str,
        rascunho_id: str,
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "DELETE",
            f"/inboxes/{segmento(caixa_id)}/drafts/{segmento(rascunho_id)}",
            **opcoes,
        )

    async def enviar(
        self,
        caixa_id: str,
        rascunho_id: str,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            f"/inboxes/{segmento(caixa_id)}/drafts/{segmento(rascunho_id)}/send",
            corpo=pedido,
            **opcoes,
        )


class CaixasAsync(RecursoBaseAsync):
    def __init__(self, transporte: TransporteAsync) -> None:
        super().__init__(transporte)
        self.conversas: ConversasCaixaAsync = ConversasCaixaAsync(transporte)
        self.etiquetas: EtiquetasCaixaAsync = EtiquetasCaixaAsync(transporte)
        self.rascunhos: RascunhosCaixaAsync = RascunhosCaixaAsync(transporte)

    async def criar(
        self,
        pedido: Mapping[str, Any],
        **opcoes: Unpack[OpcoesRequisicao],
    ) -> Resposta[Any]:
        return await self._executar(
            "POST",
            "/inboxes",
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
            "/inboxes",
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
            f"/inboxes/{segmento(id)}",
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
            f"/inboxes/{segmento(id)}",
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
            f"/inboxes/{segmento(id)}",
            **opcoes,
        )
