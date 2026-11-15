# Histórico de alterações

## 0.1.0a2 — 15/11/2026

- Instalação principal pelo PyPI, com versão explícita, e instruções locais
  separadas para desenvolvimento.
- Documentação do pacote sem mensagens transitórias de indisponibilidade;
  orientações de segurança e cobertura mantidas coerentes com a distribuição.
- Identificação da versão, verificadores de instalação e workflow manual
  alinhados à nova versão, preservando o contrato funcional do SDK.
- As evidências históricas e os artefatos da versão `0.1.0a1` permanecem intactos.

## 0.1.0a1 — 14/11/2026

Primeira versão alpha da distribuição `mailcore-sdk`, importada como
`mailcore`. Publicada no PyPI em 15/11/2026.

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
