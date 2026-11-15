"""Verificação local interoperável de webhooks HMAC-SHA256."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import math
import re
import time
from collections.abc import Mapping
from typing import cast

from .erros import ErroAssinatura
from .tipos import EventoRecebido


def _constante_invalida(_valor: str) -> None:
    raise ValueError


def verificar_assinatura(
    corpo_bruto: bytes | str,
    cabecalhos: Mapping[str, str],
    segredo: str,
    *,
    agora: float | None = None,
    tolerancia: int = 300,
) -> EventoRecebido:
    """Verifique o corpo recebido antes de interpretar JSON ou executar ações."""
    try:
        if not isinstance(corpo_bruto, (str, bytes)):
            raise ValueError
        corpo = corpo_bruto.encode("utf-8") if isinstance(corpo_bruto, str) else corpo_bruto
        if (
            len(corpo) > 8 * 1024 * 1024
            or type(tolerancia) is not int
            or not 1 <= tolerancia <= 300
        ):
            raise ValueError
        if not isinstance(segredo, str) or not segredo.startswith("whsec_") or len(segredo) > 1024:
            raise ValueError
        normalizados: dict[str, str] = {}
        for nome, valor in cabecalhos.items():
            nome = nome.lower().replace("_", "-").removeprefix("http-")
            if nome not in {"svix-id", "svix-timestamp", "svix-signature"}:
                continue
            if nome in normalizados or not isinstance(valor, str):
                raise ValueError
            normalizados[nome] = valor
        identificador = normalizados["svix-id"]
        instante = normalizados["svix-timestamp"]
        assinaturas = normalizados["svix-signature"]
        if not re.fullmatch(r"[\x21-\x7e]{1,256}", identificador) or not re.fullmatch(
            r"[1-9][0-9]{0,15}", instante
        ):
            raise ValueError
        momento = time.time() if agora is None else agora
        if (
            isinstance(momento, bool)
            or not math.isfinite(momento)
            or len(assinaturas) > 4096
            or abs(momento - int(instante)) > tolerancia
        ):
            raise ValueError
        chave = base64.b64decode(segredo[6:], validate=True)
        if len(chave) < 16:
            raise ValueError
        esperado = hmac.digest(
            chave, f"{identificador}.{instante}.".encode("ascii") + corpo, hashlib.sha256
        )
        valido = False
        for assinatura in assinaturas.split()[:32]:
            versao, separador, valor = assinatura.partition(",")
            if versao != "v1" or not separador:
                continue
            try:
                valido |= hmac.compare_digest(esperado, base64.b64decode(valor, validate=True))
            except (ValueError, binascii.Error):
                continue
        if not valido:
            raise ValueError
        evento = json.loads(corpo.decode("utf-8"), parse_constant=_constante_invalida)
        if (
            not isinstance(evento, dict)
            or not isinstance(evento.get("type"), str)
            or not isinstance(evento.get("created_at"), str)
            or "data" not in evento
        ):
            raise ValueError
        return cast(EventoRecebido, evento)
    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        UnicodeError,
        OverflowError,
        RecursionError,
    ):
        raise ErroAssinatura(
            "Não foi possível verificar a autenticidade do webhook.", codigo="assinatura_invalida"
        ) from None
