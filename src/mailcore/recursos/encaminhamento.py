"""Composição de recebidos por rotas autenticadas, sem interpretar MIME ou URLs."""

from __future__ import annotations

import base64
import json
import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Never

import anyio

from ..erros import ErroConfiguracao
from ..tipos import OpcoesRequisicao, PedidoEncaminhamentoRecebido, Resposta, RespostaEnvio
from ..transporte import Transporte, TransporteAsync
from .base import segmento

MAXIMO_ANEXOS = 10
MAXIMO_BYTES_ANEXOS = 5 * 1024 * 1024
MAXIMO_BYTES_CORPO = 500 * 1024
MAXIMO_BYTES_JSON = 8 * 1024 * 1024
MAXIMO_BYTES_DETALHE = 16 * 1024 * 1024
TIPOS_EXTENSOES = {
    "application/pdf": {"pdf"},
    "text/plain": {"txt"},
    "text/csv": {"csv"},
    "image/png": {"png"},
    "image/jpeg": {"jpg", "jpeg"},
    "image/gif": {"gif"},
    "image/webp": {"webp"},
    "message/rfc822": {"eml"},
}


def _falhar() -> Never:
    raise ErroConfiguracao("O recebido ou pedido não permite encaminhamento seguro e completo.")


def _bytes_texto(valor: str) -> int:
    try:
        return len(valor.encode("utf-8"))
    except UnicodeError:
        _falhar()


def _controles(valor: str) -> bool:
    return any(unicodedata.category(caractere) == "Cc" for caractere in valor)


def _cabecalho(valor: Any, maximo: int) -> str:
    if (
        not isinstance(valor, str)
        or not valor.strip()
        or _controles(valor)
        or _bytes_texto(valor) > maximo
    ):
        _falhar()
    return str(valor)


def _corpos(origem: Mapping[str, Any]) -> dict[str, str]:
    corpos: dict[str, str] = {}
    for campo in ("texto", "html"):
        valor = origem.get(campo)
        if valor is not None:
            if not isinstance(valor, str):
                _falhar()
            corpos[campo] = valor
    if not any(valor.strip() for valor in corpos.values()):
        _falhar()
    if sum(_bytes_texto(valor) for valor in corpos.values()) > MAXIMO_BYTES_CORPO:
        _falhar()
    return corpos


def _tamanho_json(corpo: dict[str, Any]) -> int:
    return len(json.dumps(corpo, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


@dataclass(frozen=True, repr=False)
class _Arquivo:
    caminho: str
    metadados: dict[str, str]
    tamanho: int | None


@dataclass(frozen=True, repr=False)
class _Pedido:
    caminho: str
    preservar: bool
    corpo: dict[str, Any]


def _pedido(pedido: PedidoEncaminhamentoRecebido, opcoes: OpcoesRequisicao) -> _Pedido:
    if not isinstance(pedido, Mapping) or set(pedido) - {
        "recebido_id",
        "remetente",
        "destinatarios",
        "preservar_conteudo",
        "texto",
        "html",
    }:
        _falhar()
    if set(opcoes) - {"chave_idempotencia", "tempo_limite", "limite_resposta_bytes", "cabecalhos"}:
        _falhar()
    chave = opcoes.get("chave_idempotencia")
    if chave is not None and (
        not isinstance(chave, str) or re.fullmatch(r"[\x21-\x7e]{1,256}", chave) is None
    ):
        _falhar()
    if "limite_resposta_bytes" in opcoes and (
        type(opcoes["limite_resposta_bytes"]) is not int or opcoes["limite_resposta_bytes"] < 1
    ):
        _falhar()
    recebido_id = pedido.get("recebido_id")
    if not isinstance(recebido_id, str):
        _falhar()
    caminho = f"/receiving/{segmento(recebido_id)}"
    remetente = _cabecalho(pedido.get("remetente"), 998)
    destinatarios = pedido.get("destinatarios")
    if not isinstance(destinatarios, list) or not 1 <= len(destinatarios) <= 50:
        _falhar()
    for endereco in destinatarios:
        _cabecalho(endereco, 254)
    preservar = pedido.get("preservar_conteudo", True)
    if type(preservar) is not bool:
        _falhar()
    corpo: dict[str, Any] = {"remetente": remetente, "destinatarios": list(destinatarios)}
    if preservar:
        if "texto" in pedido or "html" in pedido:
            _falhar()
    else:
        corpo.update(_corpos(pedido))
    return _Pedido(caminho, preservar, corpo)


def _arquivos(caminho: str, metadados: Any) -> list[_Arquivo]:
    if not isinstance(metadados, list) or len(metadados) > MAXIMO_ANEXOS:
        _falhar()
    arquivos = []
    ids: set[str] = set()
    cids: set[str] = set()
    total = 0
    for item in metadados:
        if not isinstance(item, Mapping):
            _falhar()
        identificador = item.get("id")
        if not isinstance(identificador, str) or identificador in ids:
            _falhar()
        id_codificado = segmento(identificador)
        ids.add(identificador)
        nome = _cabecalho(item.get("nome"), 255)
        if nome.strip() != nome or any(caractere in nome for caractere in '/\\";'):
            _falhar()
        tipo = item.get("tipo_conteudo")
        if not isinstance(tipo, str) or tipo not in TIPOS_EXTENSOES:
            _falhar()
        cid = item.get("id_conteudo")
        if cid is not None:
            if (
                not isinstance(cid, str)
                or re.fullmatch(r"[\x21-\x7e]{1,512}", cid) is None
                or any(caractere in cid for caractere in '<>"')
                or cid in cids
                or tipo == "message/rfc822"
            ):
                _falhar()
            cids.add(cid)
        extensao = nome.rsplit(".", 1)[1].lower() if "." in nome else None
        if extensao not in TIPOS_EXTENSOES[tipo] and not (
            extensao is None and cid is not None and tipo != "message/rfc822"
        ):
            _falhar()
        tamanho = item.get("tamanho")
        if type(tamanho) is not int or tamanho < 0:
            _falhar()
        total += tamanho
        if total > MAXIMO_BYTES_ANEXOS:
            _falhar()
        dados = {"nome": nome, "tipo_conteudo": tipo}
        if cid is not None:
            dados["id_conteudo"] = cid
        arquivos.append(_Arquivo(f"{caminho}/attachments/{id_codificado}/download", dados, tamanho))
    return arquivos


def _preparar(pedido: _Pedido, detalhe: Any) -> tuple[dict[str, Any], list[_Arquivo]]:
    if (
        not isinstance(detalhe, Mapping)
        or detalhe.get("conteudo_disponivel") is not True
        or detalhe.get("estado_processamento") != "concluida"
        or detalhe.get("formato_html") != "cid"
    ):
        _falhar()
    assunto = detalhe.get("assunto")
    if assunto is None or assunto == "" or isinstance(assunto, str) and not assunto.strip():
        assunto = "Sem assunto"
    assunto = _cabecalho(assunto, 998)
    if not pedido.preservar and not assunto.lower().startswith("fwd:"):
        assunto = f"Fwd: {assunto}"
    if _bytes_texto(assunto) > 998:
        _falhar()
    corpo = dict(pedido.corpo, assunto=assunto)
    if pedido.preservar:
        corpo.update(_corpos(detalhe))
        arquivos = _arquivos(pedido.caminho, detalhe.get("anexos"))
    else:
        arquivos = [
            _Arquivo(
                f"{pedido.caminho}/raw",
                {"nome": "mensagem-encaminhada.eml", "tipo_conteudo": "message/rfc822"},
                None,
            )
        ]
    if arquivos:
        corpo["anexos"] = [dict(arquivo.metadados, conteudo_base64="") for arquivo in arquivos]
    tamanho_estimado = _tamanho_json(corpo) + sum(
        4 * ((arquivo.tamanho + 2) // 3) for arquivo in arquivos if arquivo.tamanho is not None
    )
    if tamanho_estimado > MAXIMO_BYTES_JSON:
        _falhar()
    return corpo, arquivos


def _opcoes_leitura(opcoes: OpcoesRequisicao, limite_cliente: int) -> OpcoesRequisicao:
    leitura = opcoes.copy()
    leitura.pop("chave_idempotencia", None)
    leitura["limite_resposta_bytes"] = min(
        MAXIMO_BYTES_DETALHE, leitura.get("limite_resposta_bytes", limite_cliente)
    )
    return leitura


def _opcoes_arquivo(opcoes: OpcoesRequisicao, limite_cliente: int) -> OpcoesRequisicao:
    leitura = _opcoes_leitura(opcoes, limite_cliente)
    leitura["limite_resposta_bytes"] = min(
        MAXIMO_BYTES_ANEXOS, leitura.get("limite_resposta_bytes", limite_cliente)
    )
    return leitura


def _concluir_arquivo(arquivo: _Arquivo, bytes_arquivo: bytearray, total: int) -> dict[str, str]:
    if (
        total > MAXIMO_BYTES_ANEXOS
        or (arquivo.tamanho is None and not bytes_arquivo)
        or (arquivo.tamanho is not None and len(bytes_arquivo) != arquivo.tamanho)
    ):
        _falhar()
    return dict(arquivo.metadados, conteudo_base64=base64.b64encode(bytes_arquivo).decode("ascii"))


def encaminhar(
    transporte: Transporte, pedido: PedidoEncaminhamentoRecebido, opcoes: OpcoesRequisicao
) -> Resposta[RespostaEnvio]:
    validado = _pedido(pedido, opcoes)
    detalhe = transporte.executar(
        "GET",
        validado.caminho,
        consulta={"formato_html": "cid"},
        **_opcoes_leitura(opcoes, transporte._limite),
    )
    corpo, arquivos = _preparar(validado, detalhe.dados)
    total = 0
    for indice, arquivo in enumerate(arquivos):
        bytes_arquivo = bytearray()
        with transporte.fluxo(
            "GET", arquivo.caminho, **_opcoes_arquivo(opcoes, transporte._limite)
        ) as fluxo:
            for parte in fluxo:
                total += len(parte)
                if total > MAXIMO_BYTES_ANEXOS or (
                    arquivo.tamanho is not None
                    and len(bytes_arquivo) + len(parte) > arquivo.tamanho
                ):
                    _falhar()
                bytes_arquivo.extend(parte)
        corpo["anexos"][indice] = _concluir_arquivo(arquivo, bytes_arquivo, total)
    if _tamanho_json(corpo) > MAXIMO_BYTES_JSON:
        _falhar()
    return transporte.executar("POST", "/emails", corpo=corpo, **opcoes)


async def encaminhar_async(
    transporte: TransporteAsync, pedido: PedidoEncaminhamentoRecebido, opcoes: OpcoesRequisicao
) -> Resposta[RespostaEnvio]:
    validado = _pedido(pedido, opcoes)
    detalhe = await transporte.executar(
        "GET",
        validado.caminho,
        consulta={"formato_html": "cid"},
        **_opcoes_leitura(opcoes, transporte._limite),
    )
    corpo, arquivos = _preparar(validado, detalhe.dados)
    total = 0
    for indice, arquivo in enumerate(arquivos):
        bytes_arquivo = bytearray()
        async with transporte.fluxo(
            "GET", arquivo.caminho, **_opcoes_arquivo(opcoes, transporte._limite)
        ) as fluxo:
            async for parte in fluxo:
                total += len(parte)
                if total > MAXIMO_BYTES_ANEXOS or (
                    arquivo.tamanho is not None
                    and len(bytes_arquivo) + len(parte) > arquivo.tamanho
                ):
                    _falhar()
                bytes_arquivo.extend(parte)
        corpo["anexos"][indice] = _concluir_arquivo(arquivo, bytes_arquivo, total)
    if _tamanho_json(corpo) > MAXIMO_BYTES_JSON:
        _falhar()
    await anyio.lowlevel.checkpoint()
    return await transporte.executar("POST", "/emails", corpo=corpo, **opcoes)
