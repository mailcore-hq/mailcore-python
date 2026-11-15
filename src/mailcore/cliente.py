"""Clientes por instância: reutilize durante a vida da aplicação ou tarefa."""

from __future__ import annotations

from types import TracebackType
from typing import Unpack

import httpx

from . import recursos
from .tipos import ConfiguracaoCliente
from .transporte import ChaveApi, Transporte, TransporteAsync


class Cliente:
    def __init__(
        self,
        chave_api: ChaveApi = None,
        *,
        transporte_http: httpx.BaseTransport | None = None,
        **configuracao: Unpack[ConfiguracaoCliente],
    ) -> None:
        self._transporte = Transporte(chave_api, transporte_http=transporte_http, **configuracao)
        self.emails = recursos.Emails(self._transporte)
        self.lotes = recursos.Lotes(self._transporte)
        self.dominios = recursos.Dominios(self._transporte)
        self.chaves_api = recursos.ChavesApi(self._transporte)
        self.contatos = recursos.Contatos(self._transporte)
        self.segmentos = recursos.Segmentos(self._transporte)
        self.topicos = recursos.Topicos(self._transporte)
        self.propriedades_contatos = recursos.PropriedadesContatos(self._transporte)
        self.modelos = recursos.Modelos(self._transporte)
        self.webhooks = recursos.Webhooks(self._transporte)
        self.campanhas = recursos.Campanhas(self._transporte)
        self.automacoes = recursos.Automacoes(self._transporte)
        self.eventos = recursos.Eventos(self._transporte)
        self.recebimento = recursos.Recebimento(self._transporte)
        self.caixas = recursos.Caixas(self._transporte)
        self.cli = recursos.CliMailcore(self._transporte)

    def __enter__(self) -> Cliente:
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        valor: BaseException | None,
        rastreamento: TracebackType | None,
    ) -> None:
        self.fechar()

    def fechar(self) -> None:
        self._transporte.fechar()

    def __repr__(self) -> str:
        return "<Cliente credenciais=protegidas>"


class ClienteAsync:
    def __init__(
        self,
        chave_api: ChaveApi = None,
        *,
        transporte_http: httpx.AsyncBaseTransport | None = None,
        **configuracao: Unpack[ConfiguracaoCliente],
    ) -> None:
        self._transporte = TransporteAsync(
            chave_api, transporte_http=transporte_http, **configuracao
        )
        self.emails = recursos.EmailsAsync(self._transporte)
        self.lotes = recursos.LotesAsync(self._transporte)
        self.dominios = recursos.DominiosAsync(self._transporte)
        self.chaves_api = recursos.ChavesApiAsync(self._transporte)
        self.contatos = recursos.ContatosAsync(self._transporte)
        self.segmentos = recursos.SegmentosAsync(self._transporte)
        self.topicos = recursos.TopicosAsync(self._transporte)
        self.propriedades_contatos = recursos.PropriedadesContatosAsync(self._transporte)
        self.modelos = recursos.ModelosAsync(self._transporte)
        self.webhooks = recursos.WebhooksAsync(self._transporte)
        self.campanhas = recursos.CampanhasAsync(self._transporte)
        self.automacoes = recursos.AutomacoesAsync(self._transporte)
        self.eventos = recursos.EventosAsync(self._transporte)
        self.recebimento = recursos.RecebimentoAsync(self._transporte)
        self.caixas = recursos.CaixasAsync(self._transporte)
        self.cli = recursos.CliMailcoreAsync(self._transporte)

    async def __aenter__(self) -> ClienteAsync:
        return self

    async def __aexit__(
        self,
        tipo: type[BaseException] | None,
        valor: BaseException | None,
        rastreamento: TracebackType | None,
    ) -> None:
        await self.fechar()

    async def fechar(self) -> None:
        await self._transporte.fechar()

    async def fechar_async(self) -> None:
        await self.fechar()

    def __repr__(self) -> str:
        return "<ClienteAsync credenciais=protegidas>"
