# Histórico de alterações

## 0.1.0a1 — 14/11/2026

Primeira versão alpha local da distribuição `mailcore-sdk`, importada como
`mailcore`. Ainda não publicada no PyPI.

- Clientes síncrono e assíncrono com estado e pools próprios, fechamento explícito
  e suporte a `with`/`async with`.
- Dezesseis recursos principais e 151 operações por variante, com campos e nomes
  PT-BR, preservando o contrato HTTP Mailcore.
- Tipos de envio, lote, aceitação e configuração, `Resposta[T]` e marcador PEP 561.
  Entidades complexas continuam parcialmente tipadas como `Resposta[Any]`.
- Downloads autenticados, bytes e fluxos limitados; verificação local de
  assinatura sobre o corpo bruto dos webhooks.
- HTTPS verificado, redirecionamentos recusados, ausência de cookies/proxies do
  ambiente, respostas limitadas e nenhuma repetição automática.
- Exemplos opcionais Flask, FastAPI e Django com token de aplicação separado,
  envelope fixo, idempotência externa e leitura limitada.
- Verificação em Docker para a matriz CPython 3.11–3.15, testes de contrato,
  transporte HTTPS e API local isolada, sem publicação ou entrega SMTP.

`tempo_limite` segue a inatividade de cada etapa HTTPX. Ele não representa prazo
total de relógio. Consulte [a cobertura](docs/cobertura.md) para os limites e o
alcance desta versão.
