#!/bin/sh
set -eu
raiz=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
mkdir -p "$raiz/docs" "$raiz/dist"
definir_base() {
  case "$1" in
    3.11) resumo=a83ba18aef0f865b1a4a611c2cf460fe446f2795673bbb9fe43be570439e3b39 ;;
    3.12) resumo=935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df ;;
    3.13) resumo=a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72 ;;
    3.14) resumo=3fe1a0b6c2d6b2ebb572906cdabeca75aeb558c0c17db5ffefbcf8094871c32b ;;
    3.15) resumo=96599df822d0e1c6bb700014a05c7f3c8cabc6e0f7ff3c4f9f69cee033b4b5d9 ;;
  esac
  base="python:$1-slim-bookworm@sha256:$resumo"
}
for perfil in 3.11 3.12 3.13 3.14 3.15; do
  definir_base "$perfil"
  requisitos=requirements-testes-modern.txt
  if [ "$perfil" = 3.11 ]; then requisitos=requirements-testes-py311.txt; fi
  docker build --target testes --build-arg "PYTHON_IMAGE=$base" \
    --build-arg "ARQUIVO_REQUISITOS=$requisitos" --tag "mailcore/python-testes:$perfil" "$raiz"
  imagem=$(docker image inspect "mailcore/python-testes:$perfil" --format '{{.Id}}')
  docker run --rm --network none --read-only --cap-drop ALL \
    --security-opt no-new-privileges:true --memory 1g --pids-limit 128 \
    --tmpfs /tmp:rw,nosuid,size=256m,mode=1777 --user "$(id -u):$(id -g)" \
    --mount "type=bind,src=$raiz,dst=/sdk,readonly" \
    --mount "type=bind,src=$raiz/docs,dst=/relatorios" \
    --env "MAILCORE_IMAGEM_TESTE=$imagem" "$imagem" python scripts/executar_testes.py
done
docker run --rm --network none --read-only --tmpfs /tmp:rw,size=128m \
  --mount "type=bind,src=$raiz,dst=/sdk,readonly" mailcore/python-testes:3.12 \
  sh -c 'ruff check --no-cache src testes exemplos scripts && ruff format --check --no-cache src testes exemplos scripts && mypy --cache-dir /tmp/mypy src/mailcore testes/consumo_tipado.py && python scripts/gerar_recursos.py --verificar && python -m pip check'
docker build --target distribuicao --tag mailcore/python-distribuicao:local "$raiz"
container=$(docker create mailcore/python-distribuicao:local)
trap 'docker rm --force "$container" >/dev/null 2>&1 || true' EXIT HUP INT TERM
docker cp "$container:/sdk/dist/." "$raiz/dist/"
mkdir -p "$raiz/dist/dependencias"
docker cp "$container:/dependencias/." "$raiz/dist/dependencias/"
docker rm "$container" >/dev/null
trap - EXIT HUP INT TERM
for perfil in 3.11 3.12 3.13 3.14 3.15; do
  definir_base "$perfil"
  docker run --rm --network none --read-only --tmpfs /tmp:rw,nosuid,size=128m,mode=1777 \
    --user "$(id -u):$(id -g)" --env PYTHONDONTWRITEBYTECODE=1 --env PYTHONPATH=/tmp/instalado \
    --mount "type=bind,src=$raiz/dist,dst=/pacotes,readonly" \
    --mount "type=bind,src=$raiz/scripts,dst=/scripts,readonly" "$base" sh -c \
    'python -m pip install --disable-pip-version-check --no-cache-dir --no-index --find-links=/pacotes/dependencias --target /tmp/instalado /pacotes/mailcore_sdk-0.1.0a1-py3-none-any.whl && python /scripts/verificar_instalacao.py'
done
docker run --rm --network none --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$raiz/dist,dst=/pacotes" mailcore/python-distribuicao:local \
  python -c 'import hashlib,pathlib;raiz=pathlib.Path("/pacotes");[(arquivo.with_suffix(arquivo.suffix+".sha256").write_text(hashlib.sha256(arquivo.read_bytes()).hexdigest()+"  "+arquivo.name+"\n")) for arquivo in raiz.iterdir() if arquivo.suffix in {".whl",".gz"}]'
