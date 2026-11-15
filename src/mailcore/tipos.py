"""Tipos do contrato público: nomes e envelopes da API são preservados."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from dataclasses import dataclass, field
from os import PathLike
from types import MappingProxyType
from typing import (
    Any,
    Generic,
    Never,
    NotRequired,
    Protocol,
    Required,
    TypeAlias,
    TypedDict,
    TypeVar,
)

T = TypeVar("T")
Json: TypeAlias = None | bool | int | float | str | list["Json"] | dict[str, "Json"]


@dataclass(repr=False, frozen=True)
class Resposta(Generic[T]):
    dados: T
    status: int
    cabecalhos: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "cabecalhos", MappingProxyType(dict(self.cabecalhos)))

    def __getitem__(self, chave: Any) -> Any:
        return self.dados[chave]  # type: ignore[index]

    def __repr__(self) -> str:
        return f"Resposta(status={self.status})"


class OpcoesRequisicao(TypedDict, total=False):
    chave_idempotencia: str
    tempo_limite: float
    limite_resposta_bytes: int
    cabecalhos: Mapping[str, str]


class ConfiguracaoCliente(TypedDict, total=False):
    url_base: str
    tempo_limite: float
    tempo_conexao: float
    limite_resposta_bytes: int
    certificado_ca: str | PathLike[str] | None
    permitir_http_local: bool
    maximo_conexoes: int
    conexoes_ociosas: int


class AnexoEmail(TypedDict):
    nome: str
    tipo_conteudo: str
    conteudo_base64: str


class AnexoCompostoEmail(AnexoEmail):
    id_conteudo: NotRequired[str | None]


class _EnvioBasico(TypedDict, total=False):
    destinatarios: Required[list[str]]
    responder_para: str | None
    agendada_em: str | None
    tags: dict[str, str]


class _EnvioComposto(_EnvioBasico, total=False):
    remetente: Required[str]
    assunto: Required[str]
    cc: list[str]
    cco: list[str]
    cabecalhos: dict[str, str]
    anexos: list[AnexoCompostoEmail]


class EmailHtml(_EnvioComposto):
    html: str
    texto: NotRequired[str | None]


class EmailTexto(_EnvioComposto):
    texto: str
    html: NotRequired[str | None]


class ModeloEnvio(TypedDict):
    id: str
    variaveis: NotRequired[dict[str, str | int | float]]


class EmailComModelo(_EnvioBasico, total=False):
    modelo: Required[ModeloEnvio]
    remetente: str | None
    assunto: str | None
    anexos: list[AnexoEmail]
    cc: list[str]
    cco: list[str]
    cabecalhos: dict[str, str]


PedidoEmail: TypeAlias = EmailHtml | EmailTexto | EmailComModelo


class _LoteDireto(_EnvioBasico):
    remetente: str
    assunto: str
    cc: NotRequired[list[str]]
    cco: NotRequired[list[str]]
    cabecalhos: NotRequired[dict[str, str]]
    anexos: NotRequired[list[Never]]


class EmailHtmlLote(_LoteDireto):
    html: str
    texto: NotRequired[str | None]


class EmailTextoLote(_LoteDireto):
    texto: str
    html: NotRequired[str | None]


class EmailModeloLote(_EnvioBasico, total=False):
    modelo: Required[ModeloEnvio]
    remetente: str | None
    assunto: str | None
    cc: list[str]
    cco: list[str]
    cabecalhos: dict[str, str]
    anexos: list[Never]


PedidoEmailLote: TypeAlias = EmailHtmlLote | EmailTextoLote | EmailModeloLote


class RespostaEnvio(TypedDict):
    id: str
    estado: str


class RespostaLote(TypedDict):
    dados: list[RespostaEnvio]


class EventoRecebido(TypedDict):
    type: str
    created_at: str
    data: Json


class Fluxo(Protocol):
    status: int
    cabecalhos: Mapping[str, str]
    total_bytes: int

    def __iter__(self) -> Iterator[bytes]: ...
    def fechar(self) -> None: ...


class FluxoAsync(Protocol):
    status: int
    cabecalhos: Mapping[str, str]
    total_bytes: int

    def __aiter__(self) -> AsyncIterator[bytes]: ...
    async def fechar(self) -> None: ...


class GestorFluxo(Protocol):
    def __enter__(self) -> Fluxo: ...
    def __exit__(self, *argumentos: Any) -> bool | None: ...


class GestorFluxoAsync(Protocol):
    async def __aenter__(self) -> FluxoAsync: ...
    async def __aexit__(self, *argumentos: Any) -> bool | None: ...
