"""Exemplo ASGI com cliente assíncrono e leitura limitada antes do parser JSON."""

from collections.abc import Mapping
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.requests import ClientDisconnect

from exemplos.compartilhado import (
    LIMITE_CORPO,
    FalhaHttp,
    configurar,
    resumir_aceitacao,
    resumir_erro,
    validar_cabecalhos,
    validar_corpo,
)
from mailcore import ClienteAsync, Erro, ErroConfiguracao


def criar_aplicacao(*, ambiente: Mapping[str, str] | None = None, cliente: Any = None) -> FastAPI:
    configuracao = configurar(ambiente)

    @asynccontextmanager
    async def ciclo(aplicacao: FastAPI) -> Any:
        sdk = cliente if cliente is not None else ClienteAsync(**configuracao.opcoes_cliente())
        aplicacao.state.cliente_mailcore = sdk
        try:
            yield
        finally:
            if cliente is None:
                await sdk.fechar_async()

    aplicacao = FastAPI(lifespan=ciclo, docs_url=None, redoc_url=None, openapi_url=None)

    def responder(dados: dict[str, str], status: int) -> JSONResponse:
        return JSONResponse(dados, status_code=status, headers={"Cache-Control": "no-store"})

    @aplicacao.post("/enviar")
    async def enviar(requisicao: Request) -> JSONResponse:
        try:
            chave = validar_cabecalhos(
                configuracao,
                requisicao.headers.getlist("authorization"),
                requisicao.headers.getlist("idempotency-key"),
                requisicao.headers.get("content-type", ""),
            )
            corpo = bytearray()
            async for parte in requisicao.stream():
                if len(parte) > LIMITE_CORPO - len(corpo):
                    raise FalhaHttp(413, "O corpo da requisição excede o limite.")
                corpo.extend(parte)
            validar_corpo(bytes(corpo))
            resposta = await aplicacao.state.cliente_mailcore.emails.enviar(
                configuracao.pedido(),
                chave_idempotencia=chave,
            )
            return responder(resumir_aceitacao(resposta), 202)
        except FalhaHttp as erro:
            return responder({"erro": erro.mensagem}, erro.status)
        except ClientDisconnect:
            return responder({"erro": "Requisição interrompida."}, 400)
        except (Erro, ErroConfiguracao) as erro:
            dados, status = resumir_erro(erro)
            return responder(dados, status)

    return aplicacao
