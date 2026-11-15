"""Cliente Python da API Mailcore para aplicações de servidor."""

from .assinatura import verificar_assinatura
from .cliente import Cliente, ClienteAsync
from .erros import Erro, ErroApi, ErroAssinatura, ErroConfiguracao, ErroResposta, ErroTransporte
from .tipos import (
    AnexoCompostoEmail,
    AnexoEmail,
    ConfiguracaoCliente,
    EmailComModelo,
    EmailHtml,
    EmailTexto,
    EventoRecebido,
    OpcoesRequisicao,
    PedidoEmail,
    PedidoEmailLote,
    Resposta,
    RespostaEnvio,
    RespostaLote,
)
from .versao import VERSAO

__all__ = [
    "Cliente",
    "ClienteAsync",
    "Erro",
    "ErroApi",
    "ErroAssinatura",
    "ErroConfiguracao",
    "ErroResposta",
    "ErroTransporte",
    "Resposta",
    "PedidoEmail",
    "PedidoEmailLote",
    "RespostaEnvio",
    "RespostaLote",
    "AnexoEmail",
    "AnexoCompostoEmail",
    "EmailHtml",
    "EmailTexto",
    "EmailComModelo",
    "ConfiguracaoCliente",
    "OpcoesRequisicao",
    "EventoRecebido",
    "verificar_assinatura",
    "VERSAO",
]
