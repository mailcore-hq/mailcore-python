"""Erros públicos com metadados e sem reprodução de corpos de transporte."""

from collections.abc import Mapping
from types import MappingProxyType


class Erro(Exception):
    def __init__(
        self,
        mensagem: str = "Não foi possível concluir a operação.",
        *,
        codigo: str = "erro_mailcore",
        status: int | None = None,
        cabecalhos: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.status = status
        self.cabecalhos: Mapping[str, str] = MappingProxyType(dict(cabecalhos or {}))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(codigo={self.codigo!r}, status={self.status!r})"


class ErroApi(Erro):
    """Rejeição HTTP; código/mensagem públicos são preservados quando válidos."""


class ErroConfiguracao(ValueError):
    """Opções, identificadores ou JSON de entrada inválidos."""


class ErroTransporte(Erro):
    """Conexão, protocolo incompleto ou prazo de atividade excedido."""


class ErroResposta(Erro):
    """JSON inválido, codificação inesperada ou limite de resposta excedido."""


class ErroAssinatura(Erro):
    """Webhook não autenticado; nenhum detalhe do segredo é exposto."""
