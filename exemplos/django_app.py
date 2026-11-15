"""View Django que usa o cliente diretamente; não substitui django.core.mail."""

import atexit
from collections.abc import Mapping
from typing import Any

from django.core.exceptions import RequestDataTooBig
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

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


def criar_view(*, ambiente: Mapping[str, str] | None = None, cliente: Any = None) -> Any:
    configuracao = configurar(ambiente)
    sdk = cliente if cliente is not None else Cliente(**configuracao.opcoes_cliente())
    if cliente is None:
        atexit.register(sdk.fechar)

    def responder(dados: dict[str, str], status: int) -> JsonResponse:
        resposta = JsonResponse(dados, status=status)
        resposta["Cache-Control"] = "no-store"
        return resposta

    # Endpoint de máquina autenticado por Bearer; não utiliza sessão/cookie.
    @csrf_exempt
    def enviar(requisicao: HttpRequest) -> JsonResponse:
        if requisicao.method != "POST":
            resposta = responder({"erro": "Use POST para enviar."}, 405)
            resposta["Allow"] = "POST"
            return resposta
        try:
            chave = validar_cabecalhos(
                configuracao,
                [requisicao.headers.get("Authorization", "")],
                [requisicao.headers.get("Idempotency-Key", "")],
                requisicao.content_type or "",
            )
            tamanho = requisicao.META.get("CONTENT_LENGTH", "")
            if (
                str(tamanho).isascii()
                and str(tamanho).isdigit()
                and (len(str(tamanho)) > 8 or int(tamanho) > LIMITE_CORPO)
            ):
                raise FalhaHttp(413, "O corpo da requisição excede o limite.")
            validar_corpo(requisicao.read(LIMITE_CORPO + 1))
            resposta = sdk.emails.enviar(configuracao.pedido(), chave_idempotencia=chave)
            return responder(resumir_aceitacao(resposta), 202)
        except (FalhaHttp, RequestDataTooBig) as erro:
            status = erro.status if isinstance(erro, FalhaHttp) else 413
            return responder({"erro": "Não foi possível aceitar a requisição."}, status)
        except (Erro, ErroConfiguracao) as erro:
            dados, status = resumir_erro(erro)
            return responder(dados, status)

    return enviar
