"""Gera fontes estáticas de recursos a partir das rotas públicas Mailcore.

Uso de manutenção: python scripts/gerar_recursos.py [--verificar].
Nenhum código é gerado ou avaliado durante a importação da biblioteca.
A especificação corresponde ao backend e001da8 e ao SDK Node a234dc2.
"""

from __future__ import annotations

import argparse
import ast
import re
from collections import defaultdict
from pathlib import Path

ESPECIFICACAO = [
    {
        "arquivo": "emails",
        "filhos": {},
        "metodos": [
            {
                "nome": "enviar",
                "parametros": "dados",
                "verbo": "POST",
                "caminho": "/emails",
                "corpo": "dados",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/emails",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/emails/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "reagendar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/emails/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "cancelar",
                "parametros": "id",
                "verbo": "POST",
                "caminho": "/emails/#{segmento(id)}/cancel",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter_por_idempotencia",
                "parametros": "chave",
                "verbo": "GET",
                "caminho": "/emails/idempotency/#{segmento(chave)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "eventos",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/emails/#{segmento(id)}/events",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "baixar_anexo",
                "parametros": "id, indice",
                "verbo": "GET",
                "caminho": "/emails/#{segmento(id)}/attachments/#{indice}",
                "corpo": None,
                "consulta": None,
                "formato": "bytes",
                "extras": {},
            },
        ],
        "nome": "Emails",
    },
    {
        "arquivo": "emails",
        "filhos": {},
        "metodos": [
            {
                "nome": "enviar",
                "parametros": "dados",
                "verbo": "POST",
                "caminho": "/emails/batch",
                "corpo": "dados",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter_por_idempotencia",
                "parametros": "chave",
                "verbo": "GET",
                "caminho": "/emails/batch/idempotency/#{segmento(chave)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Lotes",
    },
    {
        "arquivo": "dominios",
        "filhos": {},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/domains",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/domains",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/domains/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/domains/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/domains/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "registros_dns",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/domains/#{segmento(id)}/dns",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "verificar",
                "parametros": "id",
                "verbo": "POST",
                "caminho": "/domains/#{segmento(id)}/verify",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Dominios",
    },
    {
        "arquivo": "chaves_api",
        "filhos": {},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/api-keys",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "",
                "verbo": "GET",
                "caminho": "/api-keys",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "renomear",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/api-keys/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "revogar",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/api-keys/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "ChavesApi",
    },
    {
        "arquivo": "contatos",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "contato_id",
                "verbo": "GET",
                "caminho": "/contacts/#{segmento(contato_id)}/segments",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "adicionar",
                "parametros": "contato_id, segmento_id",
                "verbo": "POST",
                "caminho": "/contacts/#{segmento(contato_id)}/segments",
                "corpo": "{ segmento_id: segmento_id }",
                "consulta": None,
                "formato": None,
                "extras": {"aceitar_vazio": "true"},
            },
            {
                "nome": "remover",
                "parametros": "contato_id, segmento_id",
                "verbo": "DELETE",
                "caminho": "/contacts/#{segmento(contato_id)}/segments/#{segmento(segmento_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "SegmentosContato",
    },
    {
        "arquivo": "contatos",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "contato_id",
                "verbo": "GET",
                "caminho": "/contacts/#{segmento(contato_id)}/topics",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "contato_id, topicos",
                "verbo": "PATCH",
                "caminho": "/contacts/#{segmento(contato_id)}/topics",
                "corpo": "{ topicos: topicos }",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "TopicosContato",
    },
    {
        "arquivo": "contatos",
        "filhos": {},
        "metodos": [
            {
                "nome": "prever",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/contacts/imports/preview",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/contacts/imports",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/contacts/imports/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "ImportacoesContatos",
    },
    {
        "arquivo": "contatos",
        "filhos": {},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "filtros = {}",
                "verbo": "POST",
                "caminho": "/contacts/exports",
                "corpo": "filtros",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/contacts/exports",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/contacts/exports/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "baixar",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/contacts/exports/#{segmento(id)}/download",
                "corpo": None,
                "consulta": None,
                "formato": "bytes",
                "extras": {},
            },
            {
                "nome": "baixar_fluxo",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/contacts/exports/#{segmento(id)}/download",
                "corpo": None,
                "consulta": None,
                "formato": "fluxo",
                "extras": {},
            },
        ],
        "nome": "ExportacoesContatos",
    },
    {
        "arquivo": "contatos",
        "filhos": {
            "segmentos": "SegmentosContato",
            "topicos": "TopicosContato",
            "importacoes": "ImportacoesContatos",
            "exportacoes": "ExportacoesContatos",
        },
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/contacts",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/contacts",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/contacts/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/contacts/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/contacts/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "adicionar_em_lote",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/contacts/batch",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "alterar_em_lote",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/contacts/bulk",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Contatos",
    },
    {
        "arquivo": "contatos",
        "filhos": {},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/segments",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/segments",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/segments/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/segments/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/segments/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Segmentos",
    },
    {
        "arquivo": "contatos",
        "filhos": {},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/topics",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/topics",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/topics/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/topics/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/topics/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Topicos",
    },
    {
        "arquivo": "contatos",
        "filhos": {},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/contact-properties",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/contact-properties",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/contact-properties/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/contact-properties/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/contact-properties/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "PropriedadesContatos",
    },
    {
        "arquivo": "modelos",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "modelo_id, filtros = {}",
                "verbo": "GET",
                "caminho": "/templates/#{segmento(modelo_id)}/versions",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "modelo_id, versao_id",
                "verbo": "GET",
                "caminho": "/templates/#{segmento(modelo_id)}/versions/#{segmento(versao_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "restaurar",
                "parametros": "modelo_id, versao_id, pedido",
                "verbo": "POST",
                "caminho": "/templates/#{segmento(modelo_id)}/versions/#{segmento(versao_id)}/restore",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "prever",
                "parametros": "modelo_id, versao_id, pedido = {}",
                "verbo": "POST",
                "caminho": "/templates/#{segmento(modelo_id)}/versions/#{segmento(versao_id)}/preview",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "VersoesModelo",
    },
    {
        "arquivo": "modelos",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "",
                "verbo": "GET",
                "caminho": "/template-folders",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/template-folders",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/template-folders/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/template-folders/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "PastasModelo",
    },
    {
        "arquivo": "modelos",
        "filhos": {"versoes": "VersoesModelo", "pastas": "PastasModelo"},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/templates",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/templates",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/templates/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/templates/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/templates/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "prever",
                "parametros": "id, pedido",
                "verbo": "POST",
                "caminho": "/templates/#{segmento(id)}/preview",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter_previa",
                "parametros": "organizacao_id, previa_id",
                "verbo": "GET",
                "caminho": "/template-previews/#{segmento(organizacao_id)}/#{segmento(previa_id)}",
                "corpo": None,
                "consulta": None,
                "formato": "texto",
                "extras": {},
            },
            {
                "nome": "testar",
                "parametros": "id, pedido",
                "verbo": "POST",
                "caminho": "/templates/#{segmento(id)}/test",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "publicar",
                "parametros": "id, pedido",
                "verbo": "POST",
                "caminho": "/templates/#{segmento(id)}/publish",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "duplicar",
                "parametros": "id, pedido = {}",
                "verbo": "POST",
                "caminho": "/templates/#{segmento(id)}/duplicate",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Modelos",
    },
    {
        "arquivo": "webhooks",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "webhook_id, filtros = {}",
                "verbo": "GET",
                "caminho": "/webhooks/#{segmento(webhook_id)}/events",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "webhook_id, evento_id",
                "verbo": "GET",
                "caminho": "/webhooks/#{segmento(webhook_id)}/events/#{segmento(evento_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar_tentativas",
                "parametros": "webhook_id, evento_id, filtros = {}",
                "verbo": "GET",
                "caminho": "/webhooks/#{segmento(webhook_id)}/events/#{segmento(evento_id)}/attempts",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "reenviar",
                "parametros": "webhook_id, evento_id",
                "verbo": "POST",
                "caminho": "/webhooks/#{segmento(webhook_id)}/events/#{segmento(evento_id)}/replay",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "EventosWebhook",
    },
    {
        "arquivo": "webhooks",
        "filhos": {"eventos": "EventosWebhook"},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/webhooks",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/webhooks",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/webhooks/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/webhooks/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/webhooks/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Webhooks",
    },
    {
        "arquivo": "campanhas",
        "filhos": {},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/broadcasts",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/broadcasts",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/broadcasts/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/broadcasts/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/broadcasts/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "duplicar",
                "parametros": "id, pedido = {}",
                "verbo": "POST",
                "caminho": "/broadcasts/#{segmento(id)}/duplicate",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "revisar",
                "parametros": "id, pedido",
                "verbo": "POST",
                "caminho": "/broadcasts/#{segmento(id)}/review",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "enviar",
                "parametros": "id, pedido",
                "verbo": "POST",
                "caminho": "/broadcasts/#{segmento(id)}/send",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "cancelar",
                "parametros": "id, pedido",
                "verbo": "POST",
                "caminho": "/broadcasts/#{segmento(id)}/cancel",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "prever",
                "parametros": "id, pedido = {}",
                "verbo": "POST",
                "caminho": "/broadcasts/#{segmento(id)}/preview",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "testar",
                "parametros": "id, pedido",
                "verbo": "POST",
                "caminho": "/broadcasts/#{segmento(id)}/test",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "ler_previa",
                "parametros": "organizacao_id, previa_id",
                "verbo": "GET",
                "caminho": "/broadcast-previews/#{segmento(organizacao_id)}/#{segmento(previa_id)}",
                "corpo": None,
                "consulta": None,
                "formato": "texto",
                "extras": {},
            },
            {
                "nome": "obter_metricas",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/broadcasts/#{segmento(id)}/metrics",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar_destinatarios",
                "parametros": "id, filtros = {}",
                "verbo": "GET",
                "caminho": "/broadcasts/#{segmento(id)}/recipients",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar_links_clicados",
                "parametros": "id, filtros = {}",
                "verbo": "GET",
                "caminho": "/broadcasts/#{segmento(id)}/clicked-links",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Campanhas",
    },
    {
        "arquivo": "automacoes",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "automacao_id, filtros = {}",
                "verbo": "GET",
                "caminho": "/automations/#{segmento(automacao_id)}/runs",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "automacao_id, execucao_id",
                "verbo": "GET",
                "caminho": "/automations/#{segmento(automacao_id)}/runs/#{segmento(execucao_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "ExecucoesAutomacoes",
    },
    {
        "arquivo": "automacoes",
        "filhos": {"execucoes": "ExecucoesAutomacoes"},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/automations",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/automations",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/automations/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/automations/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/automations/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "duplicar",
                "parametros": "id, pedido = {}",
                "verbo": "POST",
                "caminho": "/automations/#{segmento(id)}/duplicate",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "parar",
                "parametros": "id, pedido",
                "verbo": "POST",
                "caminho": "/automations/#{segmento(id)}/stop",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Automacoes",
    },
    {
        "arquivo": "eventos",
        "filhos": {},
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/events",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/events",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/events/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/events/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/events/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "enviar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/events/send",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Eventos",
    },
    {
        "arquivo": "recebimento",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/receiving",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id, filtros = {}",
                "verbo": "GET",
                "caminho": "/receiving/#{segmento(id)}",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar_anexos",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/receiving/#{segmento(id)}/attachments",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter_anexo",
                "parametros": "id, anexo_id",
                "verbo": "GET",
                "caminho": "/receiving/#{segmento(id)}/attachments/#{segmento(anexo_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "baixar_original",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/receiving/#{segmento(id)}/raw",
                "corpo": None,
                "consulta": None,
                "formato": "bytes",
                "extras": {},
            },
            {
                "nome": "baixar_anexo",
                "parametros": "id, anexo_id",
                "verbo": "GET",
                "caminho": "/receiving/#{segmento(id)}/attachments/#{segmento(anexo_id)}/download",
                "corpo": None,
                "consulta": None,
                "formato": "bytes",
                "extras": {},
            },
            {
                "nome": "baixar_original_fluxo",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/receiving/#{segmento(id)}/raw",
                "corpo": None,
                "consulta": None,
                "formato": "fluxo",
                "extras": {},
            },
            {
                "nome": "baixar_anexo_fluxo",
                "parametros": "id, anexo_id",
                "verbo": "GET",
                "caminho": "/receiving/#{segmento(id)}/attachments/#{segmento(anexo_id)}/download",
                "corpo": None,
                "consulta": None,
                "formato": "fluxo",
                "extras": {},
            },
        ],
        "nome": "Recebimento",
    },
    {
        "arquivo": "caixas",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "caixa_id, conversa_id, filtros = {}",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}/emails",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "caixa_id, conversa_id, email_id",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}/emails/#{segmento(email_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "responder",
                "parametros": "caixa_id, conversa_id, email_id, pedido",
                "verbo": "POST",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}/emails/#{segmento(email_id)}/reply",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "encaminhar",
                "parametros": "caixa_id, conversa_id, email_id, pedido",
                "verbo": "POST",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}/emails/#{segmento(email_id)}/forward",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "EmailsCaixa",
    },
    {
        "arquivo": "caixas",
        "filhos": {},
        "metodos": [
            {
                "nome": "adicionar",
                "parametros": "caixa_id, conversa_id, ids",
                "verbo": "POST",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}/labels",
                "corpo": "{ ids: ids }",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "substituir",
                "parametros": "caixa_id, conversa_id, ids",
                "verbo": "PUT",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}/labels",
                "corpo": "{ ids: ids }",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "caixa_id, conversa_id, etiqueta_id",
                "verbo": "DELETE",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}/labels/#{segmento(etiqueta_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "EtiquetasConversaCaixa",
    },
    {
        "arquivo": "caixas",
        "filhos": {"emails": "EmailsCaixa", "etiquetas": "EtiquetasConversaCaixa"},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "caixa_id, filtros = {}",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "buscar",
                "parametros": "caixa_id, filtros = {}",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/search",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "caixa_id, conversa_id",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "caixa_id, conversa_id, pedido",
                "verbo": "PATCH",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "caixa_id, conversa_id",
                "verbo": "DELETE",
                "caminho": "/inboxes/#{segmento(caixa_id)}/threads/#{segmento(conversa_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "ConversasCaixa",
    },
    {
        "arquivo": "caixas",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "caixa_id",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/labels",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "caixa_id, etiqueta_id",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/labels/#{segmento(etiqueta_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "criar",
                "parametros": "caixa_id, pedido",
                "verbo": "POST",
                "caminho": "/inboxes/#{segmento(caixa_id)}/labels",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "caixa_id, etiqueta_id, pedido",
                "verbo": "PATCH",
                "caminho": "/inboxes/#{segmento(caixa_id)}/labels/#{segmento(etiqueta_id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "caixa_id, etiqueta_id",
                "verbo": "DELETE",
                "caminho": "/inboxes/#{segmento(caixa_id)}/labels/#{segmento(etiqueta_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "EtiquetasCaixa",
    },
    {
        "arquivo": "caixas",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "caixa_id, filtros = {}",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/drafts",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "caixa_id, rascunho_id",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(caixa_id)}/drafts/#{segmento(rascunho_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "criar",
                "parametros": "caixa_id, pedido = {}",
                "verbo": "POST",
                "caminho": "/inboxes/#{segmento(caixa_id)}/drafts",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "caixa_id, rascunho_id, pedido",
                "verbo": "PATCH",
                "caminho": "/inboxes/#{segmento(caixa_id)}/drafts/#{segmento(rascunho_id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "caixa_id, rascunho_id",
                "verbo": "DELETE",
                "caminho": "/inboxes/#{segmento(caixa_id)}/drafts/#{segmento(rascunho_id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "enviar",
                "parametros": "caixa_id, rascunho_id, pedido",
                "verbo": "POST",
                "caminho": "/inboxes/#{segmento(caixa_id)}/drafts/#{segmento(rascunho_id)}/send",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "RascunhosCaixa",
    },
    {
        "arquivo": "caixas",
        "filhos": {
            "conversas": "ConversasCaixa",
            "etiquetas": "EtiquetasCaixa",
            "rascunhos": "RascunhosCaixa",
        },
        "metodos": [
            {
                "nome": "criar",
                "parametros": "pedido",
                "verbo": "POST",
                "caminho": "/inboxes",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/inboxes",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "obter",
                "parametros": "id",
                "verbo": "GET",
                "caminho": "/inboxes/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "atualizar",
                "parametros": "id, pedido",
                "verbo": "PATCH",
                "caminho": "/inboxes/#{segmento(id)}",
                "corpo": "pedido",
                "consulta": None,
                "formato": None,
                "extras": {},
            },
            {
                "nome": "remover",
                "parametros": "id",
                "verbo": "DELETE",
                "caminho": "/inboxes/#{segmento(id)}",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "Caixas",
    },
    {
        "arquivo": "cli",
        "filhos": {},
        "metodos": [
            {
                "nome": "listar",
                "parametros": "filtros = {}",
                "verbo": "GET",
                "caminho": "/cli/oauth/grants",
                "corpo": None,
                "consulta": "filtros",
                "formato": None,
                "extras": {},
            },
            {
                "nome": "revogar",
                "parametros": "id",
                "verbo": "POST",
                "caminho": "/cli/oauth/grants/#{segmento(id)}/revoke",
                "corpo": None,
                "consulta": None,
                "formato": None,
                "extras": {},
            },
        ],
        "nome": "ConcessoesCli",
    },
    {
        "arquivo": "cli",
        "filhos": {"concessoes": "ConcessoesCli"},
        "metodos": [],
        "nome": "CliMailcore",
    },
]


RAIZES = {
    "emails": "Emails",
    "lotes": "Lotes",
    "dominios": "Dominios",
    "chaves_api": "ChavesApi",
    "contatos": "Contatos",
    "segmentos": "Segmentos",
    "topicos": "Topicos",
    "propriedades_contatos": "PropriedadesContatos",
    "modelos": "Modelos",
    "webhooks": "Webhooks",
    "campanhas": "Campanhas",
    "automacoes": "Automacoes",
    "eventos": "Eventos",
    "recebimento": "Recebimento",
    "caixas": "Caixas",
    "cli": "CliMailcore",
}


def parametros_tipados(classe: str, metodo: dict) -> list[str]:
    parametros = []
    for entrada in metodo["parametros"].split(", "):
        if not entrada:
            continue
        nome = entrada.split(" = ")[0]
        opcional = " = " in entrada
        if classe == "Emails" and metodo["nome"] == "enviar":
            tipo = "PedidoEmail"
        elif classe == "Lotes" and metodo["nome"] == "enviar":
            tipo = "Sequence[PedidoEmailLote]"
        elif nome == "indice":
            tipo = "int"
        elif nome == "ids":
            tipo = "list[str]"
        elif nome == "topicos":
            tipo = "list[Mapping[str, Any]]"
        elif nome in {"pedido", "filtros", "dados", "pedidos"}:
            tipo = "Mapping[str, Any]"
        else:
            tipo = "str"
        if opcional:
            parametros.append(f"{nome}: {tipo} | None = None")
        else:
            parametros.append(f"{nome}: {tipo}")
    return parametros


def tipo_resposta(classe: str, metodo: dict, assincrono: bool) -> str:
    formato = metodo["formato"]
    if formato == "fluxo":
        return "GestorFluxoAsync" if assincrono else "GestorFluxo"
    if formato == "bytes":
        return "Resposta[bytes]"
    if formato == "texto":
        return "Resposta[str]"
    if classe == "Emails" and metodo["nome"] == "enviar":
        return "Resposta[RespostaEnvio]"
    if classe == "Lotes" and metodo["nome"] == "enviar":
        return "Resposta[RespostaLote]"
    return "Resposta[Any]"


def corpo_python(classe: str, metodo: dict) -> str | None:
    corpo = metodo["corpo"]
    if corpo == "{ segmento_id: segmento_id }":
        return '{"segmento_id": segmento_id}'
    if corpo == "{ topicos: topicos }":
        return '{"topicos": topicos}'
    if corpo == "{ ids: ids }":
        return '{"ids": ids}'
    if classe == "Lotes" and metodo["nome"] == "enviar":
        return "list(dados)"
    if corpo and f"{corpo} = {{}}" in metodo["parametros"]:
        return f"{{}} if {corpo} is None else {corpo}"
    return corpo


def emitir_metodo(classe: str, metodo: dict, assincrono: bool) -> list[str]:
    fluxo = metodo["formato"] == "fluxo"
    prefixo = "async " if assincrono and not fluxo else ""
    parametros = parametros_tipados(classe, metodo)
    retorno = tipo_resposta(classe, metodo, assincrono)
    linhas = [f"    {prefixo}def {metodo['nome']}(", "        self,"]
    linhas.extend(f"        {parametro}," for parametro in parametros)
    linhas += [
        "        **opcoes: Unpack[OpcoesRequisicao],",
        f"    ) -> {retorno}:",
    ]
    if classe == "Emails" and metodo["nome"] == "enviar":
        linhas.append(
            '        """Aceita a intenção de envio; a entrega é acompanhada separadamente."""'
        )
    if classe == "Emails" and metodo["nome"] == "baixar_anexo":
        linhas += [
            "        if isinstance(indice, bool) or not isinstance(indice, int) or indice < 0:",
            "            raise ErroConfiguracao(",
            '                "Informe um índice de anexo inteiro e não negativo."',
            "            )",
        ]
    caminho = re.sub(r"#\{([^}]+)\}", r"{\1}", metodo["caminho"])
    literal = ("f" if "#{" in metodo["caminho"] else "") + repr(caminho)
    acao = "_fluxo" if fluxo else "_executar"
    aguardar = "await " if assincrono and not fluxo else ""
    linhas += [
        f"        return {aguardar}self.{acao}(",
        f"            {metodo['verbo']!r},",
        f"            {literal},",
    ]
    corpo = corpo_python(classe, metodo)
    if corpo:
        linhas.append(f"            corpo={corpo},")
    if metodo["consulta"]:
        linhas.append(f"            consulta={metodo['consulta']},")
    if metodo["formato"] and not fluxo:
        linhas.append(f"            formato={metodo['formato']!r},")
    for nome, valor in metodo["extras"].items():
        valor = "True" if valor == "true" else valor
        linhas.append(f"            {nome}={valor},")
    linhas += ["            **opcoes,", "        )"]
    return linhas


def emitir_classe(classe: dict, assincrono: bool) -> str:
    sufixo = "Async" if assincrono else ""
    nome = classe["nome"] + sufixo
    base = "RecursoBaseAsync" if assincrono else "RecursoBase"
    linhas = [f"class {nome}({base}):"]
    if classe["filhos"]:
        transporte = "TransporteAsync" if assincrono else "Transporte"
        linhas += [
            f"    def __init__(self, transporte: {transporte}) -> None:",
            "        super().__init__(transporte)",
        ]
        for filho, tipo in classe["filhos"].items():
            linhas.append(f"        self.{filho}: {tipo}{sufixo} = {tipo}{sufixo}(transporte)")
        if classe["metodos"]:
            linhas.append("")
    for indice, metodo in enumerate(classe["metodos"]):
        if indice:
            linhas.append("")
        linhas.extend(emitir_metodo(classe["nome"], metodo, assincrono))
    return "\n".join(linhas)


def emitir_modulo(nome: str, classes: list[dict]) -> str:
    partes = [
        emitir_classe(classe, assincrono) for assincrono in (False, True) for classe in classes
    ]
    fonte = "\n\n\n".join(partes)
    colecoes = [tipo for tipo in ("Mapping", "Sequence") if f"{tipo}[" in fonte]
    tipagem = [
        tipo
        for tipo in ("TYPE_CHECKING", "Any", "Unpack")
        if tipo in fonte or (tipo == "TYPE_CHECKING" and any(c["filhos"] for c in classes))
    ]
    tipos = [
        tipo
        for tipo in (
            "GestorFluxo",
            "GestorFluxoAsync",
            "OpcoesRequisicao",
            "PedidoEmail",
            "PedidoEmailLote",
            "Resposta",
            "RespostaEnvio",
            "RespostaLote",
        )
        if re.search(rf"\b{tipo}\b", fonte)
    ]
    linhas = [
        f'"""Operações de {nome.replace("_", " ")} do contrato público Mailcore."""',
        "",
        "from __future__ import annotations",
        "",
        "# Fonte estática; manutenção em scripts/gerar_recursos.py.",
    ]
    if colecoes:
        linhas.append("from collections.abc import " + ", ".join(colecoes))
    linhas += ["from typing import " + ", ".join(tipagem), ""]
    if nome == "emails":
        linhas.append("from ..erros import ErroConfiguracao")
    linhas += ["from ..tipos import ("] + [f"    {tipo}," for tipo in tipos] + [")"]
    linhas += ["from .base import RecursoBase, RecursoBaseAsync, segmento"]
    if any(c["filhos"] for c in classes):
        linhas += [
            "",
            "if TYPE_CHECKING:",
            "    from ..transporte import Transporte, TransporteAsync",
        ]
    return "\n".join(linhas) + "\n\n\n" + fonte + "\n"


def fontes() -> dict[str, str]:
    por_arquivo: dict[str, list[dict]] = defaultdict(list)
    for classe in ESPECIFICACAO:
        por_arquivo[classe["arquivo"]].append(classe)
    resultado = {
        f"{nome}.py": emitir_modulo(nome, classes) for nome, classes in por_arquivo.items()
    }
    linhas = ['"""Recursos síncronos e assíncronos do cliente Mailcore."""', ""]
    for arquivo, classes in sorted(por_arquivo.items()):
        principais = sorted(c["nome"] for c in classes if c["nome"] in RAIZES.values())
        if principais:
            linhas += [f"from .{arquivo} import ("]
            for nome in principais:
                linhas += [f"    {nome},", f"    {nome}Async,"]
            linhas.append(")")
    linhas += ["", "__all__ = ["]
    for nome in RAIZES.values():
        linhas += [f"    {nome!r},", f"    {nome + 'Async'!r},"]
    linhas += ["]", ""]
    resultado["__init__.py"] = "\n".join(linhas)
    return resultado


def main() -> None:
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument(
        "--verificar", action="store_true", help="Confere a estrutura das fontes sem alterá-las."
    )
    opcoes = argumentos.parse_args()
    destino = Path(__file__).resolve().parents[1] / "src" / "mailcore" / "recursos"
    divergencias = []
    for nome, conteudo in fontes().items():
        caminho = destino / nome
        if opcoes.verificar:
            if not caminho.is_file() or ast.dump(
                ast.parse(caminho.read_text(encoding="utf-8"))
            ) != ast.dump(ast.parse(conteudo)):
                divergencias.append(nome)
        else:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(conteudo, encoding="utf-8")
    if divergencias:
        raise SystemExit("Fontes divergentes: " + ", ".join(divergencias))
    total = sum(len(classe["metodos"]) for classe in ESPECIFICACAO)
    print(
        f"{total} operações síncronas e {total} assíncronas conferidas."
        if opcoes.verificar
        else "Fontes de recursos preparadas."
    )


if __name__ == "__main__":
    main()
