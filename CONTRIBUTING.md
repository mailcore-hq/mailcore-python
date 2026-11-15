# Contribuir

O projeto está em alpha e distribui `mailcore-sdk`, importado como `mailcore`.
Mantenha código e documentação em português do Brasil e preserve os nomes e
envelopes do contrato público da API Mailcore.

## Implementação

- Confirme a rota, o DTO, o escopo de autorização e a resposta no backend antes
  de acrescentar uma operação. Capacidade de API não comprova uma tela ou fluxo.
- Mantenha paridade entre `Cliente` e `ClienteAsync`, sem estado global de
  credenciais. Reutilize o transporte e seus pools, em vez de criar clientes a
  cada pedido.
- Preserve omissão, `None`, `False`, revisões e envelopes de paginação. Não
  traduza valores do protocolo nem normalize DTOs diferentes para um só formato.
- Atualize os tipos públicos e a cobertura sem anunciar TypedDicts completos
  quando a resposta ainda for `Resposta[Any]`.
- Recursos gerados são mantidos pela especificação de
  `scripts/gerar_recursos.py`. Alterações nesse contrato devem atualizar a fonte
  e as duas variantes, com teste de caminho, query, corpo e retorno.

Os exemplos dos frameworks ficam separados do pacote principal. O SDK básico não
deve importar Flask, FastAPI ou Django. Mantenha testes de autenticação,
idempotência, limites e sanitização ao alterar esses exemplos.

## Verificação

Use o verificador Docker do projeto para executar formatação, lint, tipagem,
testes e empacotamento, sem instalar dependências no host. A matriz é CPython
3.11–3.15; o conjunto de frameworks respeita a compatibilidade de cada versão.
Consulte os scripts e relatórios locais para os comandos e as imagens do ensaio.

Testes que iniciam serviços devem usar rede Docker interna ou loopback do próprio
container, dados sintéticos exclusivos, nenhuma porta publicada e limpeza dos
recursos criados. Não use produção, tokens pessoais, SMTP ou contas reais nos
testes do SDK. Use CA de teste confiada explicitamente; não desative a verificação
TLS. Não publique pacotes ou aplicações durante a verificação local.

Inclua verificações pertinentes à mudança: contrato e tipos, HTTP real quando o
transporte mudar, fechamento de fluxos, cancelamento, erros sem repetição e
ausência de segredos nas respostas. Diferencie resultados de um transporte falso,
HTTPS sintético, API local e serviço de produção.

Descreva a mudança, sua motivação, as validações executadas e limites conhecidos.
Atualize `CHANGELOG.md` quando houver alteração pública. Relate problemas de
segurança conforme [SECURITY.md](SECURITY.md).
