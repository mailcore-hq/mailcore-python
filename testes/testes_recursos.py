"""Contrato dos recursos extraído independentemente do SDK Node a234dc2.

As expectativas conferem os 151 métodos por implementação, sem repetir a
especificação usada pelo gerador de fontes Python. A rede é testada à parte.
"""

from __future__ import annotations

import importlib
import inspect
import unittest
from copy import deepcopy
from unittest.mock import AsyncMock

from mailcore import recursos

CASOS = [
    {
        "classe": "ExecucoesAutomacoes",
        "metodo": "listar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/automations/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/runs",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "ExecucoesAutomacoes",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/automations/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/runs/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Automacoes",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/automations",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Automacoes",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/automations",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Automacoes",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/automations/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Automacoes",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/automations/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Automacoes",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/automations/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Automacoes",
        "metodo": "duplicar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/automations/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/duplicate",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Automacoes",
        "metodo": "parar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/automations/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/stop",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "EmailsCaixa",
        "metodo": "listar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/emails",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "EmailsCaixa",
        "metodo": "obter",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            "parte-2/ação+?@example.test",
        ],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/emails/parte-2%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "EmailsCaixa",
        "metodo": "responder",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            "parte-2/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/emails/parte-2%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/reply",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "EmailsCaixa",
        "metodo": "encaminhar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            "parte-2/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/emails/parte-2%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/forward",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "EtiquetasConversaCaixa",
        "metodo": "adicionar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            ["etiqueta-a", "etiqueta-b"],
        ],
        "verbo": "POST",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/labels",
        "kwargs": {"corpo": {"ids": ["etiqueta-a", "etiqueta-b"]}},
    },
    {
        "classe": "EtiquetasConversaCaixa",
        "metodo": "substituir",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            ["etiqueta-a", "etiqueta-b"],
        ],
        "verbo": "PUT",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/labels",
        "kwargs": {"corpo": {"ids": ["etiqueta-a", "etiqueta-b"]}},
    },
    {
        "classe": "EtiquetasConversaCaixa",
        "metodo": "remover",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            "parte-2/ação+?@example.test",
        ],
        "verbo": "DELETE",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/labels/parte-2%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "ConversasCaixa",
        "metodo": "listar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "ConversasCaixa",
        "metodo": "buscar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/search",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "ConversasCaixa",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "ConversasCaixa",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "ConversasCaixa",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/threads/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "EtiquetasCaixa",
        "metodo": "listar",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/labels",
        "kwargs": {},
    },
    {
        "classe": "EtiquetasCaixa",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/labels/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "EtiquetasCaixa",
        "metodo": "criar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/labels",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "EtiquetasCaixa",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/labels/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "EtiquetasCaixa",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/labels/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "RascunhosCaixa",
        "metodo": "listar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/drafts",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "RascunhosCaixa",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/drafts/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "RascunhosCaixa",
        "metodo": "criar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/drafts",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "RascunhosCaixa",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/drafts/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "RascunhosCaixa",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/drafts/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "RascunhosCaixa",
        "metodo": "enviar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/drafts/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/send",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Caixas",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/inboxes",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Caixas",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Caixas",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/inboxes",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Caixas",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Caixas",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/inboxes/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Campanhas",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/broadcasts",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Campanhas",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/broadcasts",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Campanhas",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Campanhas",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Campanhas",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Campanhas",
        "metodo": "duplicar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/duplicate",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Campanhas",
        "metodo": "revisar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/review",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Campanhas",
        "metodo": "enviar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/send",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Campanhas",
        "metodo": "cancelar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/cancel",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Campanhas",
        "metodo": "prever",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/preview",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Campanhas",
        "metodo": "ler_previa",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/broadcast-previews/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"formato": "texto"},
    },
    {
        "classe": "Campanhas",
        "metodo": "testar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Campanhas",
        "metodo": "obter_metricas",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/metrics",
        "kwargs": {},
    },
    {
        "classe": "Campanhas",
        "metodo": "listar_destinatarios",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/recipients",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Campanhas",
        "metodo": "listar_links_clicados",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/broadcasts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/clicked-links",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "ChavesApi",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/api-keys",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "ChavesApi",
        "metodo": "listar",
        "argumentos": [],
        "verbo": "GET",
        "caminho": "/api-keys",
        "kwargs": {},
    },
    {
        "classe": "ChavesApi",
        "metodo": "renomear",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/api-keys/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "ChavesApi",
        "metodo": "revogar",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/api-keys/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "ConcessoesCli",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/cli/oauth/grants",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "ConcessoesCli",
        "metodo": "revogar",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "POST",
        "caminho": "/cli/oauth/grants/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/revoke",
        "kwargs": {},
    },
    {
        "classe": "SegmentosContato",
        "metodo": "listar",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/contacts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/segments",
        "kwargs": {},
    },
    {
        "classe": "SegmentosContato",
        "metodo": "adicionar",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "POST",
        "caminho": "/contacts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/segments",
        "kwargs": {"aceitar_vazio": True, "corpo": {"segmento_id": "parte-1/ação+?@example.test"}},
    },
    {
        "classe": "SegmentosContato",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/contacts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/segments/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "TopicosContato",
        "metodo": "listar",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/contacts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/topics",
        "kwargs": {},
    },
    {
        "classe": "TopicosContato",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            [{"topico_id": "topico-a", "assinatura": "opt_out"}],
        ],
        "verbo": "PATCH",
        "caminho": "/contacts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/topics",
        "kwargs": {"corpo": {"topicos": [{"topico_id": "topico-a", "assinatura": "opt_out"}]}},
    },
    {
        "classe": "Contatos",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/contacts",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Contatos",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/contacts",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Contatos",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/contacts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Contatos",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/contacts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Contatos",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/contacts/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Contatos",
        "metodo": "adicionar_em_lote",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/contacts/batch",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Contatos",
        "metodo": "alterar_em_lote",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/contacts/bulk",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "ExportacoesContatos",
        "metodo": "criar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "POST",
        "caminho": "/contacts/exports",
        "kwargs": {
            "corpo": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "ExportacoesContatos",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/contacts/exports",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "ExportacoesContatos",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/contacts/exports/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "ExportacoesContatos",
        "metodo": "baixar",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/contacts/exports/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/download",
        "kwargs": {"formato": "bytes"},
    },
    {
        "classe": "ExportacoesContatos",
        "metodo": "baixar_fluxo",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/contacts/exports/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/download",
        "kwargs": {"formato": "fluxo"},
    },
    {
        "classe": "ImportacoesContatos",
        "metodo": "prever",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/contacts/imports/preview",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "ImportacoesContatos",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/contacts/imports",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "ImportacoesContatos",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/contacts/imports/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Segmentos",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/segments",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Segmentos",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/segments",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Segmentos",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/segments/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Segmentos",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/segments/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Segmentos",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/segments/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Topicos",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/topics",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Topicos",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/topics",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Topicos",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/topics/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Topicos",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/topics/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Topicos",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/topics/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "PropriedadesContatos",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/contact-properties",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "PropriedadesContatos",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/contact-properties",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "PropriedadesContatos",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/contact-properties/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "PropriedadesContatos",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/contact-properties/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "PropriedadesContatos",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/contact-properties/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Dominios",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/domains",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Dominios",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/domains",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Dominios",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/domains/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Dominios",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/domains/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Dominios",
        "metodo": "registros_dns",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/domains/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/dns",
        "kwargs": {},
    },
    {
        "classe": "Dominios",
        "metodo": "verificar",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "POST",
        "caminho": "/domains/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/verify",
        "kwargs": {},
    },
    {
        "classe": "Dominios",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/domains/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Emails",
        "metodo": "enviar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/emails",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Emails",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/emails",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Emails",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/emails/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Emails",
        "metodo": "reagendar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/emails/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Emails",
        "metodo": "cancelar",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "POST",
        "caminho": "/emails/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/cancel",
        "kwargs": {},
    },
    {
        "classe": "Emails",
        "metodo": "obter_por_idempotencia",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/emails/idempotency/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Emails",
        "metodo": "eventos",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/emails/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/events",
        "kwargs": {},
    },
    {
        "classe": "Emails",
        "metodo": "baixar_anexo",
        "argumentos": ["parte-0/ação+?@example.test", 2],
        "verbo": "GET",
        "caminho": "/emails/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/attachments/2",
        "kwargs": {"formato": "bytes"},
    },
    {
        "classe": "Lotes",
        "metodo": "enviar",
        "argumentos": [[{"texto": "ação", "opcional": None, "ativo": False}]],
        "verbo": "POST",
        "caminho": "/emails/batch",
        "kwargs": {"corpo": [{"texto": "ação", "opcional": None, "ativo": False}]},
    },
    {
        "classe": "Lotes",
        "metodo": "obter_por_idempotencia",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/emails/batch/idempotency/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Eventos",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/events",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Eventos",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/events",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Eventos",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/events/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Eventos",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/events/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Eventos",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/events/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Eventos",
        "metodo": "enviar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/events/send",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "VersoesModelo",
        "metodo": "listar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/versions",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "VersoesModelo",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/versions/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "VersoesModelo",
        "metodo": "restaurar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/versions/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/restore",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "VersoesModelo",
        "metodo": "prever",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/versions/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/preview",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "PastasModelo",
        "metodo": "listar",
        "argumentos": [],
        "verbo": "GET",
        "caminho": "/template-folders",
        "kwargs": {},
    },
    {
        "classe": "PastasModelo",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/template-folders",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "PastasModelo",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/template-folders/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "PastasModelo",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/template-folders/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Modelos",
        "metodo": "prever",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/preview",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Modelos",
        "metodo": "obter_previa",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/template-previews/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"formato": "texto"},
    },
    {
        "classe": "Modelos",
        "metodo": "testar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Modelos",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/templates",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Modelos",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/templates",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Modelos",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Modelos",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Modelos",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Modelos",
        "metodo": "publicar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/publish",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Modelos",
        "metodo": "duplicar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "POST",
        "caminho": "/templates/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/duplicate",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Recebimento",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/receiving",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Recebimento",
        "metodo": "obter",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/receiving/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Recebimento",
        "metodo": "listar_anexos",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/receiving/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/attachments",
        "kwargs": {},
    },
    {
        "classe": "Recebimento",
        "metodo": "obter_anexo",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/receiving/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/attachments/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Recebimento",
        "metodo": "baixar_original",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/receiving/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/raw",
        "kwargs": {"formato": "bytes"},
    },
    {
        "classe": "Recebimento",
        "metodo": "baixar_anexo",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/receiving/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/attachments/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/download",
        "kwargs": {"formato": "bytes"},
    },
    {
        "classe": "Recebimento",
        "metodo": "baixar_original_fluxo",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/receiving/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/raw",
        "kwargs": {"formato": "fluxo"},
    },
    {
        "classe": "Recebimento",
        "metodo": "baixar_anexo_fluxo",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/receiving/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/attachments/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/download",
        "kwargs": {"formato": "fluxo"},
    },
    {
        "classe": "EventosWebhook",
        "metodo": "listar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/webhooks/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/events",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "EventosWebhook",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/webhooks/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/events/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "EventosWebhook",
        "metodo": "listar_tentativas",
        "argumentos": [
            "parte-0/ação+?@example.test",
            "parte-1/ação+?@example.test",
            {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None},
        ],
        "verbo": "GET",
        "caminho": "/webhooks/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/events/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/attempts",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "EventosWebhook",
        "metodo": "reenviar",
        "argumentos": ["parte-0/ação+?@example.test", "parte-1/ação+?@example.test"],
        "verbo": "POST",
        "caminho": "/webhooks/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/events/parte-1%2Fa%C3%A7%C3%A3o%2B%3F%40example.test/replay",
        "kwargs": {},
    },
    {
        "classe": "Webhooks",
        "metodo": "criar",
        "argumentos": [{"texto": "ação", "opcional": None, "ativo": False}],
        "verbo": "POST",
        "caminho": "/webhooks",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Webhooks",
        "metodo": "listar",
        "argumentos": [{"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}],
        "verbo": "GET",
        "caminho": "/webhooks",
        "kwargs": {
            "consulta": {"limite": 2, "antes": "cursor/ação", "ativo": False, "opcional": None}
        },
    },
    {
        "classe": "Webhooks",
        "metodo": "obter",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "GET",
        "caminho": "/webhooks/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
    {
        "classe": "Webhooks",
        "metodo": "atualizar",
        "argumentos": [
            "parte-0/ação+?@example.test",
            {"texto": "ação", "opcional": None, "ativo": False},
        ],
        "verbo": "PATCH",
        "caminho": "/webhooks/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {"corpo": {"texto": "ação", "opcional": None, "ativo": False}},
    },
    {
        "classe": "Webhooks",
        "metodo": "remover",
        "argumentos": ["parte-0/ação+?@example.test"],
        "verbo": "DELETE",
        "caminho": "/webhooks/parte-0%2Fa%C3%A7%C3%A3o%2B%3F%40example.test",
        "kwargs": {},
    },
]


MODULOS = {
    "Emails": "emails",
    "Lotes": "emails",
    "Dominios": "dominios",
    "ChavesApi": "chaves_api",
    "SegmentosContato": "contatos",
    "TopicosContato": "contatos",
    "ImportacoesContatos": "contatos",
    "ExportacoesContatos": "contatos",
    "Contatos": "contatos",
    "Segmentos": "contatos",
    "Topicos": "contatos",
    "PropriedadesContatos": "contatos",
    "VersoesModelo": "modelos",
    "PastasModelo": "modelos",
    "Modelos": "modelos",
    "EventosWebhook": "webhooks",
    "Webhooks": "webhooks",
    "Campanhas": "campanhas",
    "ExecucoesAutomacoes": "automacoes",
    "Automacoes": "automacoes",
    "Eventos": "eventos",
    "Recebimento": "recebimento",
    "EmailsCaixa": "caixas",
    "EtiquetasConversaCaixa": "caixas",
    "ConversasCaixa": "caixas",
    "EtiquetasCaixa": "caixas",
    "RascunhosCaixa": "caixas",
    "Caixas": "caixas",
    "ConcessoesCli": "cli",
    "CliMailcore": "cli",
}
FILHOS = {
    "Contatos": ["segmentos", "topicos", "importacoes", "exportacoes"],
    "Modelos": ["versoes", "pastas"],
    "Webhooks": ["eventos"],
    "Automacoes": ["execucoes"],
    "Caixas": ["conversas", "etiquetas", "rascunhos"],
    "ConversasCaixa": ["emails", "etiquetas"],
    "CliMailcore": ["concessoes"],
}
OPCOES = {
    "chave_idempotencia": "negocio-123",
    "tempo_limite": 2.5,
    "limite_resposta_bytes": 4096,
    "cabecalhos": {"X-Correlacao": "sintetica"},
}


def obter_classe(nome: str, assincrono: bool = False) -> type:
    modulo = importlib.import_module("mailcore.recursos." + MODULOS[nome])
    return getattr(modulo, nome + ("Async" if assincrono else ""))


class FluxoColetor:
    def __init__(self) -> None:
        self.entradas = 0
        self.saidas = 0

    def __enter__(self):
        self.entradas += 1
        return self

    def __exit__(self, *_erro) -> None:
        self.saidas += 1

    def __iter__(self):
        yield b"primeira"
        yield b"segunda"


class FluxoColetorAsync:
    def __init__(self) -> None:
        self.entradas = 0
        self.saidas = 0

    async def __aenter__(self):
        self.entradas += 1
        return self

    async def __aexit__(self, *_erro) -> None:
        self.saidas += 1

    async def __aiter__(self):
        yield b"primeira"
        yield b"segunda"


class TransporteColetor:
    def __init__(self) -> None:
        self.chamadas = []
        self.retorno = object()
        self.retorno_fluxo = FluxoColetor()

    def executar(
        self,
        metodo,
        caminho,
        *,
        corpo=None,
        consulta=None,
        formato="json",
        aceitar_vazio=False,
        **opcoes,
    ):
        self.chamadas.append(
            {
                "metodo": metodo,
                "caminho": caminho,
                "corpo": deepcopy(corpo),
                "consulta": deepcopy(consulta),
                "formato": formato,
                "aceitar_vazio": aceitar_vazio,
                "opcoes": deepcopy(opcoes),
            }
        )
        return self.retorno

    def fluxo(self, metodo, caminho, *, formato="fluxo", **opcoes):
        self.executar(metodo, caminho, formato=formato, **opcoes)
        return self.retorno_fluxo


class TransporteColetorAsync:
    def __init__(self) -> None:
        self.chamadas = []
        self.retorno = object()
        self.retorno_fluxo = FluxoColetorAsync()
        self.executar = AsyncMock(side_effect=self.registrar)

    def registrar(
        self,
        metodo,
        caminho,
        *,
        corpo=None,
        consulta=None,
        formato="json",
        aceitar_vazio=False,
        **opcoes,
    ):
        self.chamadas.append(
            {
                "metodo": metodo,
                "caminho": caminho,
                "corpo": deepcopy(corpo),
                "consulta": deepcopy(consulta),
                "formato": formato,
                "aceitar_vazio": aceitar_vazio,
                "opcoes": deepcopy(opcoes),
            }
        )
        return self.retorno

    def fluxo(self, metodo, caminho, *, formato="fluxo", **opcoes):
        self.registrar(metodo, caminho, formato=formato, **opcoes)
        return self.retorno_fluxo


def chamada_esperada(caso: dict) -> dict:
    return {
        "metodo": caso["verbo"],
        "caminho": caso["caminho"],
        "corpo": None,
        "consulta": None,
        "formato": "json",
        "aceitar_vazio": False,
        "opcoes": OPCOES,
    } | caso["kwargs"]


def caso_sincrono(caso: dict):
    def verificar(self):
        transporte = TransporteColetor()
        recurso = obter_classe(caso["classe"])(transporte)
        argumentos = deepcopy(caso["argumentos"])
        metodo = getattr(recurso, caso["metodo"])
        self.assertFalse(inspect.iscoroutinefunction(metodo))
        retorno = metodo(*argumentos, **deepcopy(OPCOES))
        if caso["kwargs"].get("formato") == "fluxo":
            self.assertIs(transporte.retorno_fluxo, retorno)
            with retorno as fluxo:
                self.assertEqual([b"primeira", b"segunda"], list(fluxo))
            self.assertEqual((1, 1), (retorno.entradas, retorno.saidas))
        else:
            self.assertIs(transporte.retorno, retorno)
        self.assertEqual([chamada_esperada(caso)], transporte.chamadas)
        self.assertEqual(caso["argumentos"], argumentos)

    return verificar


def caso_assincrono(caso: dict):
    async def verificar(self):
        transporte = TransporteColetorAsync()
        recurso = obter_classe(caso["classe"], True)(transporte)
        argumentos = deepcopy(caso["argumentos"])
        metodo = getattr(recurso, caso["metodo"])
        if caso["kwargs"].get("formato") == "fluxo":
            self.assertFalse(inspect.iscoroutinefunction(metodo))
            retorno = metodo(*argumentos, **deepcopy(OPCOES))
            self.assertIs(transporte.retorno_fluxo, retorno)
            async with retorno as fluxo:
                partes = [parte async for parte in fluxo]
                self.assertEqual([b"primeira", b"segunda"], partes)
            self.assertEqual((1, 1), (retorno.entradas, retorno.saidas))
            transporte.executar.assert_not_awaited()
        else:
            self.assertTrue(inspect.iscoroutinefunction(metodo))
            retorno = await metodo(*argumentos, **deepcopy(OPCOES))
            self.assertIs(transporte.retorno, retorno)
            transporte.executar.assert_awaited_once()
        self.assertEqual([chamada_esperada(caso)], transporte.chamadas)
        self.assertEqual(caso["argumentos"], argumentos)

    return verificar


def percorrer_filhos(recurso):
    nome = type(recurso).__name__.removesuffix("Async")
    for filho in FILHOS.get(nome, []):
        objeto = getattr(recurso, filho)
        yield objeto
        yield from percorrer_filhos(objeto)


class TestesRecursos(unittest.TestCase):
    def test_todos_os_metodos_estao_no_contrato_independente(self):
        self.assertEqual(151, len(CASOS))
        por_classe = {}
        for caso in CASOS:
            por_classe.setdefault(caso["classe"], set()).add(caso["metodo"])
        for nome, esperados in por_classe.items():
            for assincrono in (False, True):
                classe = obter_classe(nome, assincrono)
                encontrados = {
                    nome_metodo
                    for nome_metodo, valor in vars(classe).items()
                    if not nome_metodo.startswith("_") and inspect.isfunction(valor)
                }
                self.assertEqual(esperados, encontrados, classe.__name__)

    def test_recursos_raiz_exportam_clientes_sync_e_async(self):
        nomes = {
            "Emails",
            "Lotes",
            "Dominios",
            "ChavesApi",
            "Contatos",
            "Segmentos",
            "Topicos",
            "PropriedadesContatos",
            "Modelos",
            "Webhooks",
            "Campanhas",
            "Automacoes",
            "Eventos",
            "Recebimento",
            "Caixas",
            "CliMailcore",
        }
        self.assertEqual(32, len(recursos.__all__))
        for nome in nomes:
            self.assertIs(obter_classe(nome), getattr(recursos, nome))
            self.assertIs(obter_classe(nome, True), getattr(recursos, nome + "Async"))

    def test_recursos_aninhados_encaminham_operacoes_ao_transporte_do_pai(self):
        transporte = TransporteColetor()
        for nome in ("Contatos", "Modelos", "Webhooks", "Automacoes", "Caixas", "CliMailcore"):
            raiz = obter_classe(nome)(transporte)
            for objeto in percorrer_filhos(raiz):
                self.assertFalse(type(objeto).__name__.endswith("Async"))
                caso = next(caso for caso in CASOS if caso["classe"] == type(objeto).__name__)
                retorno = getattr(objeto, caso["metodo"])(*deepcopy(caso["argumentos"]))
                self.assertIs(transporte.retorno, retorno)
        self.assertEqual(14, len(transporte.chamadas))

    def test_consultas_omitem_filtros_padrao_e_corpos_opcionais_usam_objeto_novo(self):
        transporte = TransporteColetor()
        obter_classe("Emails")(transporte).listar()
        obter_classe("Recebimento")(transporte).obter("email")
        self.assertIsNone(transporte.chamadas[0]["consulta"])
        self.assertIsNone(transporte.chamadas[1]["consulta"])
        chamadas = [
            (obter_classe("ExportacoesContatos")(transporte).criar, []),
            (obter_classe("Modelos")(transporte).duplicar, ["modelo"]),
            (obter_classe("VersoesModelo")(transporte).prever, ["modelo", "versao"]),
            (obter_classe("Campanhas")(transporte).prever, ["campanha"]),
            (obter_classe("Automacoes")(transporte).duplicar, ["automacao"]),
            (obter_classe("RascunhosCaixa")(transporte).criar, ["caixa"]),
        ]
        for metodo, argumentos in chamadas:
            metodo(*argumentos)
            self.assertEqual({}, transporte.chamadas[-1]["corpo"])

    def test_indices_de_anexo_recusam_booleanos_ou_valores_nao_inteiros(self):
        transporte = TransporteColetor()
        emails = obter_classe("Emails")(transporte)
        for indice in (-1, 1.5, "0", None, True, False):
            with self.assertRaises(ValueError):
                emails.baixar_anexo("email", indice)
        self.assertEqual([], transporte.chamadas)

    def test_ids_invalidos_nao_chegam_ao_transporte(self):
        transporte = TransporteColetor()
        emails = obter_classe("Emails")(transporte)
        for id_recurso in (None, "", ".", "..", "linha\nquebrada", "controle\x00"):
            with self.assertRaises(ValueError):
                emails.obter(id_recurso)
        self.assertEqual([], transporte.chamadas)

    def test_lote_aceita_sequencia_sem_alterar_a_tupla_ou_os_pedidos(self):
        transporte = TransporteColetor()
        pedidos = ({"remetente": "origem@example.test", "html": "<p>Olá</p>"},)
        copia = deepcopy(pedidos)
        obter_classe("Lotes")(transporte).enviar(pedidos)
        self.assertEqual(list(pedidos), transporte.chamadas[0]["corpo"])
        self.assertEqual(copia, pedidos)


class TestesRecursosAsync(unittest.IsolatedAsyncioTestCase):
    async def test_recursos_aninhados_aguardam_o_transporte_assincrono_do_pai(self):
        transporte = TransporteColetorAsync()
        for nome in ("Contatos", "Modelos", "Webhooks", "Automacoes", "Caixas", "CliMailcore"):
            raiz = obter_classe(nome, True)(transporte)
            for objeto in percorrer_filhos(raiz):
                self.assertTrue(type(objeto).__name__.endswith("Async"))
                nome_classe = type(objeto).__name__.removesuffix("Async")
                caso = next(caso for caso in CASOS if caso["classe"] == nome_classe)
                retorno = await getattr(objeto, caso["metodo"])(*deepcopy(caso["argumentos"]))
                self.assertIs(transporte.retorno, retorno)
        self.assertEqual(14, transporte.executar.await_count)
        self.assertEqual(14, len(transporte.chamadas))

    async def test_indices_e_ids_invalidos_nao_criam_pedidos_assincronos(self):
        transporte = TransporteColetorAsync()
        emails = obter_classe("Emails", True)(transporte)
        for indice in (-1, 1.5, "0", None, True, False):
            with self.assertRaises(ValueError):
                await emails.baixar_anexo("email", indice)
        for id_recurso in (None, "", ".", "..", "linha\nquebrada", "controle\x00"):
            with self.assertRaises(ValueError):
                await emails.obter(id_recurso)
        transporte.executar.assert_not_awaited()
        self.assertEqual([], transporte.chamadas)

    async def test_corpos_opcionais_async_nao_sao_compartilhados_entre_chamadas(self):
        transporte = TransporteColetorAsync()
        modelos = obter_classe("Modelos", True)(transporte)
        await modelos.duplicar("primeiro")
        await modelos.duplicar("segundo")
        self.assertEqual({}, transporte.chamadas[0]["corpo"])
        self.assertEqual({}, transporte.chamadas[1]["corpo"])
        self.assertEqual(2, transporte.executar.await_count)


for _caso in CASOS:
    _nome = "test_contrato_" + _caso["classe"] + "_" + _caso["metodo"]
    setattr(TestesRecursos, _nome, caso_sincrono(_caso))
    setattr(TestesRecursosAsync, _nome, caso_assincrono(_caso))


if __name__ == "__main__":
    unittest.main()
