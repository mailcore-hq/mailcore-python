ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
FROM ${PYTHON_IMAGE} AS testes
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates openssl git && rm -rf /var/lib/apt/lists/*
COPY --from=docker:29-cli@sha256:5a7af0dcb0e46c803efe9b45371dd21cb500e5b4453250394ac6f06d49b6e6f1 /usr/local/bin/docker /usr/local/bin/docker
WORKDIR /sdk
ARG ARQUIVO_REQUISITOS=requirements-testes-modern.txt
COPY requirements* ./
RUN python -m pip install --no-cache-dir -r ${ARQUIVO_REQUISITOS} && python -m pip check
COPY . .
RUN python -m pip install --no-deps --no-build-isolation -e .
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python", "-m", "unittest", "discover", "-s", "testes", "-p", "testes_*.py"]

FROM testes AS distribuicao
RUN python -m build --no-isolation
RUN python -m pip download --only-binary=:all: --constraint requirements-testes-modern.txt --dest /dependencias httpx==0.28.1 anyio==4.16.0 typing_extensions==4.16.0
