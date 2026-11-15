"""Contrato das rotas demonstrativas: mensagem fixa, autenticação e limites."""

import hashlib
import hmac
import json
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from mailcore import ErroApi

LIMITE_CORPO = 4096


class FalhaHttp(Exception):
    def __init__(self, status: int, mensagem: str) -> None:
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem


@dataclass(frozen=True, repr=False)
class ConfiguracaoExemplo:
    chave_api: str
    resumo_token: bytes
    remetente: str
    destinatario: str
    url_base: str | None

    def opcoes_cliente(self) -> dict[str, Any]:
        opcoes: dict[str, Any] = {"chave_api": self.chave_api}
        if self.url_base is not None:
            opcoes["url_base"] = self.url_base
        return opcoes

    def pedido(self) -> dict[str, Any]:
        return {
            "remetente": self.remetente,
            "destinatarios": [self.destinatario],
            "assunto": "Mensagem de exemplo",
            "texto": "Integração Mailcore com Python.",
        }


def configurar(ambiente: Mapping[str, str] | None = None) -> ConfiguracaoExemplo:
    origem = os.environ if ambiente is None else ambiente
    chave = origem.get("MAILCORE_API_KEY")
    token = origem.get("TOKEN_APLICACAO")
    remetente = origem.get("MAILCORE_REMETENTE")
    destinatario = origem.get("MAILCORE_DESTINATARIO")
    if not (
        isinstance(chave, str)
        and re.fullmatch(r"[\x21-\x7e]{1,512}", chave)
        and isinstance(token, str)
        and re.fullmatch(r"[A-Za-z0-9_-]{43,256}", token)
        and all(
            isinstance(valor, str)
            and re.fullmatch(r"[^\x00-\x1f\x7f]{1,320}", valor)
            and valor.strip() == valor
            for valor in (remetente, destinatario)
        )
    ):
        raise ValueError("Configure as credenciais e os endereços fixos da aplicação.")
    resumo = hashlib.sha256(token.encode("ascii")).digest()
    if hmac.compare_digest(resumo, hashlib.sha256(chave.encode("ascii")).digest()):
        raise ValueError("Use credenciais diferentes para a aplicação e a API.")
    url = origem.get("MAILCORE_API_URL")
    if url is not None and (
        not isinstance(url, str) or not url.startswith("https://") or any(ord(c) <= 32 for c in url)
    ):
        raise ValueError("Configure uma URL base HTTPS válida para a API.")
    return ConfiguracaoExemplo(chave, resumo, remetente, destinatario, url)


def validar_cabecalhos(
    configuracao: ConfiguracaoExemplo,
    autorizacoes: Sequence[str],
    idempotencias: Sequence[str],
    tipo_conteudo: str,
) -> str:
    autorizacao = autorizacoes[0] if len(autorizacoes) == 1 else ""
    correspondencia = re.fullmatch(r"Bearer ([A-Za-z0-9_-]{43,256})", autorizacao)
    if correspondencia is None or not hmac.compare_digest(
        hashlib.sha256(correspondencia[1].encode("ascii")).digest(), configuracao.resumo_token
    ):
        raise FalhaHttp(401, "Acesso não autorizado.")
    chave = idempotencias[0] if len(idempotencias) == 1 else ""
    if not re.fullmatch(r"[\x21-\x7e]{1,256}", chave) or "," in chave:
        raise FalhaHttp(400, "Informe uma chave de idempotência válida.")
    if tipo_conteudo.split(";", 1)[0].strip().lower() != "application/json":
        raise FalhaHttp(415, "Envie um objeto JSON.")
    return chave


def validar_corpo(corpo: bytes) -> None:
    if len(corpo) > LIMITE_CORPO:
        raise FalhaHttp(413, "O corpo da requisição excede o limite.")

    def recusar_constante(_valor: str) -> None:
        raise ValueError("Constante não permitida em JSON.")

    try:
        valor = json.loads(corpo.decode("utf-8"), parse_constant=recusar_constante)
        if not isinstance(valor, dict):
            raise ValueError("Objeto JSON obrigatório.")
    except (ValueError, UnicodeError, RecursionError):
        raise FalhaHttp(400, "Envie um objeto JSON válido em UTF-8.") from None


def resumir_aceitacao(resposta: Any) -> dict[str, str]:
    dados = resposta.dados
    if not (
        resposta.status == 202
        and isinstance(dados, dict)
        and isinstance(dados.get("id"), str)
        and dados["id"]
        and isinstance(dados.get("estado"), str)
        and dados["estado"]
    ):
        raise FalhaHttp(502, "Resposta de aceitação inválida.")
    return {"id": dados["id"], "estado": dados["estado"]}


def resumir_erro(erro: Exception) -> tuple[dict[str, str], int]:
    status = getattr(erro, "status", None)
    if isinstance(erro, ErroApi) and isinstance(status, int) and 400 <= status <= 599:
        return {"erro": "Não foi possível aceitar a mensagem."}, status
    return {"erro": "Não foi possível confirmar a aceitação da mensagem."}, 502
