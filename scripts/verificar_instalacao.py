"""Confere a wheel em Python mínimo sem frameworks e sem checkout no sys.path."""

import importlib.metadata
import json
import pathlib
import sys

import mailcore

assert importlib.metadata.version("mailcore-sdk") == mailcore.VERSAO == "0.2.0a1"
assert "/tmp/instalado/" in str(mailcore.__file__)
assert pathlib.Path(mailcore.__file__).with_name("py.typed").is_file()
assert all(nome not in sys.modules for nome in ["flask", "fastapi", "django"])
with mailcore.Cliente("mc_instalacao_sintetica") as cliente:
    assert cliente.contatos.exportacoes and cliente.caixas.conversas.emails
    assert callable(cliente.recebimento.encaminhar)
assert mailcore.PedidoEncaminhamentoRecebido
print(
    json.dumps(
        {
            "resultado": "aprovado",
            "python": sys.version.split()[0],
            "versao": mailcore.VERSAO,
            "frameworks_carregados": False,
        }
    )
)
