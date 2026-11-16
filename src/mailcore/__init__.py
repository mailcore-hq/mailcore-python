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
    EncaminhamentoHtml,
    EncaminhamentoPreservado,
    EncaminhamentoTexto,
    EventoRecebido,
    OpcoesRequisicao,
    PedidoEmail,
    PedidoEmailLote,
    PedidoEncaminhamentoRecebido,
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
    "PedidoEncaminhamentoRecebido",
    "EncaminhamentoHtml",
    "EncaminhamentoPreservado",
    "EncaminhamentoTexto",
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
