"""HTTP síncrono/assíncrono com pools isolados, TLS e leitura limitada."""

from __future__ import annotations

import json
import math
import os
import re
import ssl
from collections.abc import AsyncIterator, Callable, Iterator, Mapping
from contextlib import asynccontextmanager, contextmanager
from http.cookiejar import CookieJar, DefaultCookiePolicy
from typing import Any, TypeAlias
from urllib.parse import urlencode, urlsplit

import anyio
import httpx

from .erros import ErroApi, ErroConfiguracao, ErroResposta, ErroTransporte
from .tipos import Resposta
from .versao import VERSAO

ChaveApi: TypeAlias = str | Callable[[], str] | None
RESERVADOS = frozenset(
    {
        "authorization",
        "proxy-authorization",
        "cookie",
        "host",
        "content-length",
        "content-type",
        "accept",
        "connection",
        "transfer-encoding",
        "idempotency-key",
        "user-agent",
        "accept-encoding",
    }
)
OMITIDOS = frozenset({"set-cookie", "authorization", "proxy-authorization"})


class _SemCookies(DefaultCookiePolicy):
    def set_ok(self, *argumentos: Any, **opcoes: Any) -> bool:
        return False

    def return_ok(self, *argumentos: Any, **opcoes: Any) -> bool:
        return False


def _tempo(valor: float) -> float:
    if (
        isinstance(valor, bool)
        or not isinstance(valor, (int, float))
        or not 0 < valor <= 86_400
        or not math.isfinite(valor)
    ):
        raise ErroConfiguracao("O prazo deve ser positivo e finito, em segundos, até 86400.")
    return float(valor)


def _limite(valor: int) -> int:
    if type(valor) is not int or valor < 1:
        raise ErroConfiguracao("O limite de resposta deve ser um inteiro positivo em bytes.")
    return valor


def _texto(valor: str) -> None:
    try:
        valor.encode("utf-8")
    except UnicodeError:
        raise ErroConfiguracao("O texto deve ser UTF-8 válido.") from None


def _normalizar_json(valor: Any, profundidade: int = 0) -> Any:
    if profundidade > 100:
        raise ErroConfiguracao("O corpo JSON excede a profundidade permitida.")
    if isinstance(valor, Mapping):
        normalizado = {}
        for nome, item in valor.items():
            if not isinstance(nome, str):
                raise ErroConfiguracao("As chaves do JSON devem ser strings.")
            _texto(nome)
            normalizado[nome] = _normalizar_json(item, profundidade + 1)
        return normalizado
    elif isinstance(valor, (list, tuple)):
        return [_normalizar_json(item, profundidade + 1) for item in valor]
    elif isinstance(valor, str):
        _texto(valor)
    elif isinstance(valor, float):
        if not math.isfinite(valor):
            raise ErroConfiguracao("Números JSON devem ser finitos.")
    elif valor is not None and not isinstance(valor, (bool, int)):
        raise ErroConfiguracao("O corpo deve conter somente valores JSON.")
    return valor


def _constante_invalida(_valor: str) -> Any:
    raise ValueError("Constante JSON inválida.")


def _ler_json(corpo: bytes) -> Any:
    return json.loads(corpo.decode("utf-8"), parse_constant=_constante_invalida)


def _metadados(resposta: httpx.Response) -> dict[str, str]:
    return {nome: valor for nome, valor in resposta.headers.items() if nome.lower() not in OMITIDOS}


def _erro_rede(
    erro: httpx.RequestError, cabecalhos: Mapping[str, str] | None = None
) -> ErroTransporte:
    if isinstance(erro, httpx.TimeoutException):
        return ErroTransporte(
            "Uma etapa HTTP excedeu o prazo de atividade.",
            codigo="prazo_excedido",
            cabecalhos=cabecalhos,
        )
    return ErroTransporte(
        "Não foi possível concluir a comunicação com a API.",
        codigo="falha_de_rede",
        cabecalhos=cabecalhos,
    )


def _validar_resposta(resposta: httpx.Response, limite: int) -> None:
    status, cabecalhos = resposta.status_code, _metadados(resposta)
    if 300 <= status <= 399:
        raise ErroApi(
            "A API respondeu com um redirecionamento recusado.",
            codigo="redirecionamento_recusado",
            status=status,
            cabecalhos=cabecalhos,
        )
    # Pedimos identity: nunca devolva gzip como se fossem bytes MIME/CSV originais.
    codificacao = resposta.headers.get("content-encoding", "identity").strip().lower()
    if codificacao not in {"", "identity"}:
        raise ErroResposta(
            "A API respondeu com uma codificação não negociada.",
            codigo="codificacao_inesperada",
            status=status,
            cabecalhos=cabecalhos,
        )
    tamanho = resposta.headers.get("content-length")
    if tamanho is not None:
        if not re.fullmatch(r"[0-9]+", tamanho):
            raise ErroResposta(
                "Tamanho HTTP inválido.",
                codigo="resposta_invalida",
                status=status,
                cabecalhos=cabecalhos,
            )
        if int(tamanho) > limite:
            _excedida(resposta)


def _excedida(resposta: httpx.Response) -> None:
    raise ErroResposta(
        "A resposta excedeu o limite de bytes configurado.",
        codigo="resposta_excedida",
        status=resposta.status_code,
        cabecalhos=_metadados(resposta),
    )


def _interpretar(
    resposta: httpx.Response, corpo: bytes, formato: str, aceitar_vazio: bool
) -> Resposta[Any]:
    status, cabecalhos = resposta.status_code, _metadados(resposta)
    if not 200 <= status <= 299:
        try:
            envelope = _ler_json(corpo)
            erro = envelope.get("erro") if isinstance(envelope, dict) else None
            if (
                isinstance(erro, dict)
                and isinstance(erro.get("codigo"), str)
                and isinstance(erro.get("mensagem"), str)
            ):
                raise ErroApi(
                    erro["mensagem"], codigo=erro["codigo"], status=status, cabecalhos=cabecalhos
                )
        except (ValueError, UnicodeError, RecursionError):
            pass
        raise ErroApi(
            "A API retornou erro HTTP sem detalhes JSON válidos.",
            codigo="erro_http",
            status=status,
            cabecalhos=cabecalhos,
        )
    dados: Any
    if formato == "bytes":
        dados = corpo
    elif not corpo and (status == 204 or aceitar_vazio):
        dados = None
    else:
        try:
            dados = corpo.decode("utf-8") if formato == "texto" else _ler_json(corpo)
        except (ValueError, UnicodeError, RecursionError):
            raise ErroResposta(
                "A API retornou uma resposta inválida.",
                codigo="resposta_invalida",
                status=status,
                cabecalhos=cabecalhos,
            ) from None
    return Resposta(dados, status, cabecalhos)


class _Configuracao:
    def __init__(
        self,
        chave_api: ChaveApi = None,
        *,
        url_base: str = "https://mailcore.com.br/v1",
        tempo_limite: float = 30,
        tempo_conexao: float = 10,
        limite_resposta_bytes: int = 16 * 1024 * 1024,
        certificado_ca: str | os.PathLike[str] | None = None,
        permitir_http_local: bool = False,
        maximo_conexoes: int = 100,
        conexoes_ociosas: int = 20,
    ) -> None:
        self._chave_api = chave_api
        if chave_api is not None and not callable(chave_api):
            self._validar_chave(chave_api)
        try:
            url = urlsplit(url_base)
            local = url.hostname in {"localhost", "127.0.0.1", "::1"}
            if (
                not url.hostname
                or url.username
                or url.password
                or url.query
                or url.fragment
                or (
                    url.scheme != "https"
                    and not (url.scheme == "http" and local and permitir_http_local is True)
                )
            ):
                raise ValueError
            _ = url.port
            self._base = str(httpx.URL(url_base.rstrip("/")))
        except (ValueError, TypeError, httpx.InvalidURL):
            raise ErroConfiguracao(
                "Use URL base HTTPS sem credenciais, parâmetros ou fragmentos."
            ) from None
        self._tempo = _tempo(tempo_limite)
        self._conexao = _tempo(tempo_conexao)
        self._limite = _limite(limite_resposta_bytes)
        if (
            type(maximo_conexoes) is not int
            or maximo_conexoes < 1
            or type(conexoes_ociosas) is not int
            or not 0 <= conexoes_ociosas <= maximo_conexoes
        ):
            raise ErroConfiguracao("Informe limites de conexões inteiros e coerentes.")
        self._limites_pool = httpx.Limits(
            max_connections=maximo_conexoes, max_keepalive_connections=conexoes_ociosas
        )
        try:
            self._ssl = ssl.create_default_context(cafile=certificado_ca)
            self._ssl.minimum_version = ssl.TLSVersion.TLSv1_2
        except (OSError, ValueError, TypeError, ssl.SSLError):
            raise ErroConfiguracao(
                "Não foi possível carregar a autoridade certificadora."
            ) from None

    def __repr__(self) -> str:
        return f"<{type(self).__name__} credenciais=protegidas>"

    @staticmethod
    def _validar_chave(chave: Any) -> str:
        if not isinstance(chave, str) or not re.fullmatch(r"[\x21-\x7e]+", chave):
            raise ErroConfiguracao("Informe a chave de API Mailcore ou configure MAILCORE_API_KEY.")
        return chave

    def _resolver_chave(self) -> str:
        try:
            if self._chave_api is None:
                chave = os.environ.get("MAILCORE_API_KEY")
            else:
                chave = self._chave_api() if callable(self._chave_api) else self._chave_api
            return self._validar_chave(chave)
        except Exception:
            raise ErroConfiguracao("Não foi possível obter uma chave de API válida.") from None

    def _preparar(
        self,
        metodo: str,
        caminho: str,
        *,
        corpo: Any = None,
        consulta: Mapping[str, Any] | None = None,
        formato: str = "json",
        tempo_limite: float | None = None,
        limite_resposta_bytes: int | None = None,
        chave_idempotencia: str | None = None,
        cabecalhos: Mapping[str, str] | None = None,
    ) -> tuple[httpx.Request, int]:
        if metodo not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise ErroConfiguracao("Método HTTP inválido.")
        if formato not in {"json", "texto", "bytes", "fluxo"}:
            raise ErroConfiguracao("Formato de resposta inválido.")
        if (
            not isinstance(caminho, str)
            or not caminho.startswith("/")
            or caminho.startswith("//")
            or re.search(r"[?#\\\x00-\x20]", caminho)
            or any(parte in {".", ".."} for parte in caminho.split("/"))
        ):
            raise ErroConfiguracao("Caminho de recurso inválido.")
        if consulta is not None and not isinstance(consulta, Mapping):
            raise ErroConfiguracao("A consulta deve ser um mapeamento de valores simples.")
        if cabecalhos is not None and not isinstance(cabecalhos, Mapping):
            raise ErroConfiguracao("Cabeçalhos devem ser um mapeamento textual.")
        pares = []
        for nome, valor in (consulta or {}).items():
            if valor is None:
                continue
            if (
                not isinstance(nome, str)
                or not isinstance(valor, (str, bool, int, float))
                or isinstance(valor, float)
                and not math.isfinite(valor)
            ):
                raise ErroConfiguracao("A consulta deve conter valores simples e nomes textuais.")
            valor = "true" if valor is True else "false" if valor is False else str(valor)
            _texto(nome)
            _texto(valor)
            pares.append((nome, valor))
        url = self._base + caminho + ("?" + urlencode(pares) if pares else "")
        recebidos = dict(cabecalhos or {})
        for nome, valor in recebidos.items():
            if (
                not isinstance(nome, str)
                or not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", nome)
                or nome.lower() in RESERVADOS
                or not isinstance(valor, str)
                or not re.fullmatch(r"[\x20-\x7e]*", valor)
            ):
                raise ErroConfiguracao("Cabeçalho inválido ou reservado pelo SDK.")
        recebidos.update(
            {
                "Accept": "application/octet-stream"
                if formato in {"bytes", "fluxo"}
                else "text/html"
                if formato == "texto"
                else "application/json",
                "Accept-Encoding": "identity",
                "User-Agent": f"mailcore-python/{VERSAO}",
                "Authorization": f"Bearer {self._resolver_chave()}",
            }
        )
        if chave_idempotencia is not None:
            if not isinstance(chave_idempotencia, str) or not re.fullmatch(
                r"[\x21-\x7e]{1,256}", chave_idempotencia
            ):
                raise ErroConfiguracao(
                    "A chave de idempotência deve ter de 1 a 256 caracteres ASCII visíveis."
                )
            recebidos["Idempotency-Key"] = chave_idempotencia
        conteudo = None
        if corpo is not None:
            normalizado = _normalizar_json(corpo)
            try:
                conteudo = json.dumps(
                    normalizado, ensure_ascii=False, allow_nan=False, separators=(",", ":")
                ).encode("utf-8")
            except (TypeError, ValueError, UnicodeError, RecursionError):
                raise ErroConfiguracao("O corpo não é serializável como JSON.") from None
            if len(conteudo) > 50 * 1024 * 1024:
                raise ErroConfiguracao("O corpo JSON ultrapassa 50 MiB.")
            recebidos["Content-Type"] = "application/json"
        tempo = self._tempo if tempo_limite is None else _tempo(tempo_limite)
        limite = self._limite if limite_resposta_bytes is None else _limite(limite_resposta_bytes)
        pedido = httpx.Request(metodo, url, headers=recebidos, content=conteudo)
        pedido.extensions["timeout"] = httpx.Timeout(
            tempo, connect=min(tempo, self._conexao)
        ).as_dict()
        return pedido, limite


class _Fluxo:
    def __init__(self, resposta: httpx.Response, limite: int) -> None:
        self._resposta = resposta
        self._limite = limite
        self._consumido = False
        self._fechado = False
        self._em_memoria = resposta.content if resposta.is_stream_consumed else None
        self.total_bytes = 0
        self.status = resposta.status_code
        self.cabecalhos = Resposta(None, self.status, _metadados(resposta)).cabecalhos

    def __repr__(self) -> str:
        return f"<{type(self).__name__} status={self.status} bytes={self.total_bytes}>"

    def _contar(self, parte: bytes) -> None:
        self.total_bytes += len(parte)
        if self.total_bytes > self._limite:
            _excedida(self._resposta)

    def _conferir_tamanho(self) -> None:
        esperado = self._resposta.headers.get("content-length")
        if esperado is not None and int(esperado) != self.total_bytes:
            raise ErroTransporte(
                "A resposta terminou com tamanho divergente.",
                codigo="resposta_incompleta",
                status=self.status,
                cabecalhos=self.cabecalhos,
            )


class Fluxo(_Fluxo):
    def __iter__(self) -> Iterator[bytes]:
        if (
            self._consumido
            or self._fechado
            or (self._resposta.is_closed and self._em_memoria is None)
        ):
            raise ErroConfiguracao("O fluxo já foi consumido ou encerrado.")
        self._consumido = True
        try:
            partes = (
                (self._em_memoria,) if self._em_memoria is not None else self._resposta.iter_raw()
            )
            for parte in partes:
                self._contar(parte)
                if parte:
                    yield parte
            self._conferir_tamanho()
        except httpx.RequestError as erro:
            raise _erro_rede(erro, self.cabecalhos) from None

    def fechar(self) -> None:
        self._fechado = True
        self._resposta.close()


class FluxoAsync(_Fluxo):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        if (
            self._consumido
            or self._fechado
            or (self._resposta.is_closed and self._em_memoria is None)
        ):
            raise ErroConfiguracao("O fluxo já foi consumido ou encerrado.")
        self._consumido = True
        try:
            if self._em_memoria is not None:
                self._contar(self._em_memoria)
                if self._em_memoria:
                    yield self._em_memoria
                self._conferir_tamanho()
                return
            async for parte in self._resposta.aiter_raw():
                self._contar(parte)
                if parte:
                    yield parte
            self._conferir_tamanho()
        except httpx.RequestError as erro:
            raise _erro_rede(erro, self.cabecalhos) from None

    async def fechar(self) -> None:
        self._fechado = True
        with anyio.CancelScope(shield=True):
            await self._resposta.aclose()


class Transporte(_Configuracao):
    def __init__(
        self,
        chave_api: ChaveApi = None,
        *,
        transporte_http: httpx.BaseTransport | None = None,
        **opcoes: Any,
    ) -> None:
        super().__init__(chave_api, **opcoes)
        transporte = (
            transporte_http
            if transporte_http is not None
            else httpx.HTTPTransport(
                verify=self._ssl, trust_env=False, retries=0, limits=self._limites_pool
            )
        )
        self._http = httpx.Client(
            transport=transporte,
            trust_env=False,
            follow_redirects=False,
            cookies=CookieJar(policy=_SemCookies()),
        )

    @contextmanager
    def fluxo(
        self, metodo: str, caminho: str, *, aceitar_vazio: bool = False, **opcoes: Any
    ) -> Iterator[Fluxo]:
        if self._http.is_closed:
            raise ErroConfiguracao("O cliente já foi encerrado.")
        pedido, limite = self._preparar(metodo, caminho, **opcoes)
        resposta = None
        leitor = None
        try:
            try:
                resposta = self._http.send(pedido, stream=True, follow_redirects=False)
            except httpx.RequestError as erro:
                raise _erro_rede(erro) from None
            _validar_resposta(resposta, limite)
            leitor = Fluxo(resposta, limite)
            if not 200 <= resposta.status_code <= 299:
                _interpretar(resposta, b"".join(leitor), "json", aceitar_vazio)
            yield leitor
        finally:
            if leitor is not None:
                leitor.fechar()
            elif resposta is not None:
                resposta.close()

    def executar(
        self,
        metodo: str,
        caminho: str,
        *,
        formato: str = "json",
        aceitar_vazio: bool = False,
        **opcoes: Any,
    ) -> Resposta[Any]:
        with self.fluxo(
            metodo, caminho, formato=formato, aceitar_vazio=aceitar_vazio, **opcoes
        ) as leitor:
            corpo = b"".join(leitor)
            return _interpretar(leitor._resposta, corpo, formato, aceitar_vazio)

    def fechar(self) -> None:
        self._http.close()


class TransporteAsync(_Configuracao):
    def __init__(
        self,
        chave_api: ChaveApi = None,
        *,
        transporte_http: httpx.AsyncBaseTransport | None = None,
        **opcoes: Any,
    ) -> None:
        super().__init__(chave_api, **opcoes)
        transporte = (
            transporte_http
            if transporte_http is not None
            else httpx.AsyncHTTPTransport(
                verify=self._ssl, trust_env=False, retries=0, limits=self._limites_pool
            )
        )
        self._http = httpx.AsyncClient(
            transport=transporte,
            trust_env=False,
            follow_redirects=False,
            cookies=CookieJar(policy=_SemCookies()),
        )

    @asynccontextmanager
    async def fluxo(
        self, metodo: str, caminho: str, *, aceitar_vazio: bool = False, **opcoes: Any
    ) -> AsyncIterator[FluxoAsync]:
        if self._http.is_closed:
            raise ErroConfiguracao("O cliente já foi encerrado.")
        pedido, limite = self._preparar(metodo, caminho, **opcoes)
        resposta = None
        leitor = None
        try:
            try:
                resposta = await self._http.send(pedido, stream=True, follow_redirects=False)
            except httpx.RequestError as erro:
                raise _erro_rede(erro) from None
            _validar_resposta(resposta, limite)
            leitor = FluxoAsync(resposta, limite)
            if not 200 <= resposta.status_code <= 299:
                corpo = b"".join([parte async for parte in leitor])
                _interpretar(resposta, corpo, "json", aceitar_vazio)
            yield leitor
        finally:
            if leitor is not None:
                await leitor.fechar()
            elif resposta is not None:
                with anyio.CancelScope(shield=True):
                    await resposta.aclose()

    async def executar(
        self,
        metodo: str,
        caminho: str,
        *,
        formato: str = "json",
        aceitar_vazio: bool = False,
        **opcoes: Any,
    ) -> Resposta[Any]:
        async with self.fluxo(
            metodo, caminho, formato=formato, aceitar_vazio=aceitar_vazio, **opcoes
        ) as leitor:
            corpo = b"".join([parte async for parte in leitor])
            return _interpretar(leitor._resposta, corpo, formato, aceitar_vazio)

    async def fechar(self) -> None:
        with anyio.CancelScope(shield=True):
            await self._http.aclose()
