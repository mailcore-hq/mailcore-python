"""Exemplo WSGI: construir uma vez por worker e enviar somente a mensagem fixa."""

import atexit
from collections.abc import Mapping
from typing import Any

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from exemplos.compartilhado import (
    LIMITE_CORPO,
    FalhaHttp,
    configurar,
    resumir_aceitacao,
    resumir_erro,
    validar_cabecalhos,
    validar_corpo,
)
from mailcore import Cliente, Erro, ErroConfiguracao


def criar_aplicacao(*, ambiente: Mapping[str, str] | None = None, cliente: Any = None) -> Flask:
    configuracao = configurar(ambiente)
    sdk = cliente if cliente is not None else Cliente(**configuracao.opcoes_cliente())
    if cliente is None:
        atexit.register(sdk.fechar)
    aplicacao = Flask(__name__, static_folder=None)
    aplicacao.config.update(MAX_CONTENT_LENGTH=LIMITE_CORPO, DEBUG=False)

    @aplicacao.after_request
    def proteger_cache(resposta: Any) -> Any:
        resposta.headers["Cache-Control"] = "no-store"
        return resposta

    @aplicacao.post("/enviar")
    def enviar() -> Any:
        chave = validar_cabecalhos(
            configuracao,
            request.headers.getlist("Authorization"),
            request.headers.getlist("Idempotency-Key"),
            request.content_type or "",
        )
        validar_corpo(request.stream.read(LIMITE_CORPO + 1))
        resposta = sdk.emails.enviar(configuracao.pedido(), chave_idempotencia=chave)
        return jsonify(resumir_aceitacao(resposta)), 202

    @aplicacao.errorhandler(FalhaHttp)
    def falha_http(erro: FalhaHttp) -> Any:
        return jsonify(erro=erro.mensagem), erro.status

    @aplicacao.errorhandler(HTTPException)
    def falha_framework(erro: HTTPException) -> Any:
        return jsonify(erro="Requisição não permitida."), erro.code or 400

    def falha_sdk(erro: Exception) -> Any:
        dados, status = resumir_erro(erro)
        return jsonify(dados), status

    aplicacao.register_error_handler(Erro, falha_sdk)
    aplicacao.register_error_handler(ErroConfiguracao, falha_sdk)
    return aplicacao
