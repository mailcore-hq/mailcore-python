"""Executa a suíte e grava somente contagens e versões, sem corpos ou credenciais."""

import importlib.metadata
import io
import json
import os
import platform
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
saida = io.StringIO()
suite = unittest.defaultTestLoader.discover("testes", pattern="testes_*.py")
resultado = unittest.TextTestRunner(stream=saida, verbosity=1).run(suite)
relatorio = {
    "data_utc": datetime.now(timezone.utc).isoformat(),
    "resultado": "aprovado" if resultado.wasSuccessful() and not resultado.skipped else "falhou",
    "python": platform.python_version(),
    "plataforma": platform.platform(),
    "imagem": os.environ.get("MAILCORE_IMAGEM_TESTE"),
    "testes": resultado.testsRun,
    "falhas": len(resultado.failures),
    "erros": len(resultado.errors),
    "ignorados": len(resultado.skipped),
    "versoes": {
        nome: importlib.metadata.version(nome)
        for nome in ["mailcore-sdk", "httpx", "anyio", "Flask", "fastapi", "Django"]
    },
    "rede_externa": False,
    "portas_publicadas": False,
    "smtp": False,
}
destino = (
    Path(os.environ.get("MAILCORE_RELATORIOS", "/relatorios"))
    / f"python-{platform.python_version()}.json"
)
temporario = destino.with_suffix(f".{os.getpid()}.tmp")
temporario.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n")
temporario.replace(destino)
print(json.dumps(relatorio, ensure_ascii=False))
if relatorio["resultado"] != "aprovado":
    print(saida.getvalue(), file=sys.stderr)
    raise SystemExit(1)
