"""Recursos síncronos e assíncronos do cliente Mailcore."""

from .automacoes import (
    Automacoes,
    AutomacoesAsync,
)
from .caixas import (
    Caixas,
    CaixasAsync,
)
from .campanhas import (
    Campanhas,
    CampanhasAsync,
)
from .chaves_api import (
    ChavesApi,
    ChavesApiAsync,
)
from .cli import (
    CliMailcore,
    CliMailcoreAsync,
)
from .contatos import (
    Contatos,
    ContatosAsync,
    PropriedadesContatos,
    PropriedadesContatosAsync,
    Segmentos,
    SegmentosAsync,
    Topicos,
    TopicosAsync,
)
from .dominios import (
    Dominios,
    DominiosAsync,
)
from .emails import (
    Emails,
    EmailsAsync,
    Lotes,
    LotesAsync,
)
from .eventos import (
    Eventos,
    EventosAsync,
)
from .modelos import (
    Modelos,
    ModelosAsync,
)
from .recebimento import (
    Recebimento,
    RecebimentoAsync,
)
from .webhooks import (
    Webhooks,
    WebhooksAsync,
)

__all__ = [
    "Emails",
    "EmailsAsync",
    "Lotes",
    "LotesAsync",
    "Dominios",
    "DominiosAsync",
    "ChavesApi",
    "ChavesApiAsync",
    "Contatos",
    "ContatosAsync",
    "Segmentos",
    "SegmentosAsync",
    "Topicos",
    "TopicosAsync",
    "PropriedadesContatos",
    "PropriedadesContatosAsync",
    "Modelos",
    "ModelosAsync",
    "Webhooks",
    "WebhooksAsync",
    "Campanhas",
    "CampanhasAsync",
    "Automacoes",
    "AutomacoesAsync",
    "Eventos",
    "EventosAsync",
    "Recebimento",
    "RecebimentoAsync",
    "Caixas",
    "CaixasAsync",
    "CliMailcore",
    "CliMailcoreAsync",
]
