# Segurança

Esta distribuição está em alpha.
O pacote de distribuição é `mailcore-sdk`; o módulo importado é `mailcore`.
As linhas CPython adotadas na matriz são 3.11–3.15, com versões corrigidas das
dependências do projeto.

## Relatar um problema

Comunique vulnerabilidades por um canal privado acordado com
os mantenedores. Informe versão, comportamento observado, impacto e uma reprodução
mínima com dados sintéticos. Não inclua chaves, segredos de webhook, MIME de
clientes, destinatários reais ou URLs temporárias de download em relatos públicos.
Não há prazo de resposta ou correção garantido nesta etapa alpha.

## Proteções e responsabilidades

O transporte padrão verifica TLS, aceita CA privada, recusa redirecionamentos,
solicita `identity`, recusa outra codificação e não usa cookies ou proxies do
ambiente. A opção de HTTP é explícita e limitada a loopback. Transportes injetados
para testes ou integração têm sua política de rede sob responsabilidade de quem
os configura.

O limite padrão de resposta é 16 MiB, também durante downloads e erros. O teto de
JSON de pedido é 50 MiB; ele não substitui o limite de CSV de 8 MiB ou limites
menores dos endpoints. Os timeouts HTTPX são por inatividade de etapa, não um
prazo total. Nenhum timeout ou cancelamento comprova que um envio foi desfeito.

Use chaves somente no servidor, com o menor escopo necessário. Preserve uma chave
de idempotência estável para repetir explicitamente uma intenção. Separe clientes
e credenciais entre organizações. Feche pools e respostas em fluxo pelos gestores
de contexto; evite registrar corpos, dados pessoais ou cabeçalhos de autenticação.

Verifique webhooks antes de interpretar seus efeitos, usando o corpo bruto e o
segredo correto. A janela de timestamp não substitui a deduplicação do
identificador do evento na aplicação. Original e anexos recebidos devem ser
tratados como conteúdo externo; a disponibilidade obedece à retenção do servidor.
Os downloads do SDK usam rotas autenticadas e não navegam automaticamente nas
URLs temporárias contidas nos metadados.

Os exemplos HTTP exigem um token próprio e enviam uma mensagem fixa. A aplicação
que os hospedar continua responsável por entrada HTTPS, limites do servidor,
autorização de negócio, proteção de logs e gestão de segredos.
