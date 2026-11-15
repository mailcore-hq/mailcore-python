# Cobertura do SDK Python

A versão `0.1.0a2`, distribuída como `mailcore-sdk` e importada como `mailcore`,
oferece **16 recursos principais, 30 classes e 151 operações por variante**.
`Cliente` e `ClienteAsync` totalizam 60 classes de recursos e 302 métodos. As duas
variantes acessam o mesmo contrato HTTP; esses números não representam 302 rotas
distintas. A versão alpha não oferece garantia de estabilidade da API pública.

A superfície preserva o contrato dos SDKs Mailcore Ruby e Node. O
[ensaio de API local](integracao-api.json) identifica a revisão do backend e o
SHA256 das fontes usados na validação. Revisão Git e hash de conteúdo são
identificadores distintos; o relatório registra o estado do ensaio, não uma
afirmação sobre o HEAD atual do backend.

## Recursos

Os caminhos abaixo partem de uma instância de `Cliente` ou `ClienteAsync`.

| Recurso principal       | Superfície incluída                                                                    | Operações por variante |
| ----------------------- | -------------------------------------------------------------------------------------- | ---------------------: |
| `emails`                | Enviar, listar, obter, reagendar, cancelar, eventos, consulta por idempotência e anexo |                      8 |
| `lotes`                 | Enviar e consultar por idempotência                                                    |                      2 |
| `dominios`              | CRUD, capacidades, tracking, registros DNS e verificação                               |                      7 |
| `chaves_api`            | Criar, listar, renomear e revogar                                                      |                      4 |
| `contatos`              | CRUD, lote, segmentos, tópicos, importações e exportações                              |                     20 |
| `segmentos`             | Criar, listar, obter, atualizar e remover                                              |                      5 |
| `topicos`               | Criar, listar, obter, atualizar e remover                                              |                      5 |
| `propriedades_contatos` | Criar, listar, obter, atualizar e remover                                              |                      5 |
| `modelos`               | CRUD, publicação, duplicação, prévias, testes, versões e pastas                        |                     18 |
| `webhooks`              | CRUD, eventos, tentativas e reenvio                                                    |                      9 |
| `campanhas`             | CRUD, duplicação, revisão, envio/cancelamento, prévias, testes e métricas              |                     15 |
| `automacoes`            | CRUD, duplicação, parada e consulta de execuções                                       |                      9 |
| `eventos`               | Definição, consulta, edição, remoção, listagem e envio de ocorrência                   |                      6 |
| `recebimento`           | Consulta, anexos, original MIME e downloads comuns ou em fluxo                         |                      8 |
| `caixas`                | CRUD, etiquetas, conversas, mensagens, respostas, encaminhamento e rascunhos           |                     28 |
| `cli`                   | Listar e revogar concessões                                                            |                      2 |
| **Total**               | **151 operações com a mesma superfície nas duas variantes**                            |                **151** |

Os recursos subordinados usam propriedades, como `contatos.exportacoes`,
`modelos.versoes`, `webhooks.eventos`, `caixas.conversas.emails` e `cli.concessoes`.
Os nomes dos métodos permanecem iguais no cliente assíncrono: use
`await cliente.emails.enviar(...)`, sem sufixo adicional no nome.

## Pedidos, respostas e tipagem

Pedidos e filtros aceitam `Mapping` com os campos em português do DTO HTTP, como
`remetente`, `destinatarios`, `agendada_em` e `revisao`. Opções de transporte são
argumentos nomeados, como `chave_idempotencia`, `tempo_limite` e
`limite_resposta_bytes`. O servidor continua responsável pelas regras de negócio,
permissões, revisões e limites específicos de cada endpoint.

O transporte aceita valores JSON: chaves String, texto UTF-8, números finitos,
booleanos, listas, tuplas convertidas em arrays, mapeamentos e `None`. Objetos
arbitrários, bytes em campos JSON e números não finitos são recusados. Um campo
omitido difere de um campo enviado com `None`; `None` e `False` permanecem no corpo.
Na query, `None` é omitido e `False` é enviado como `false`. Identificadores são
codificados como segmentos, preservando o prefixo da API.

As respostas usam `Resposta[T]`, com `dados`, `status` e `cabecalhos` separados.
JSON mantém chaves String, inclusive nos objetos internos; resposta sem conteúdo
pode produzir `dados=None`. Downloads comuns retornam `Resposta[bytes]` e prévias
textuais usam `str`. `resposta["id"]` consulta o campo em `dados`.

Há tipos públicos para envio direto/modelo, anexos, lote, respostas de aceitação,
configuração e opções, além do marcador PEP 561 `py.typed`. Entre eles estão
`PedidoEmail`, `PedidoEmailLote`, `RespostaEnvio` e `RespostaLote`. Essa tipagem não
é um schema completo de todas as entidades: recursos complexos ainda aceitam
`Mapping[str, Any]` e retornam `Resposta[Any]`, preservando o DTO do servidor.
TypedDict não substitui a validação de runtime nem a validação da API.

A paginação é explícita: uma chamada consulta uma página e conserva o envelope e
os cursores recebidos. O SDK não percorre páginas automaticamente nem uniformiza
envelopes distintos do backend.

## Contratos relevantes

- Envio direto permite composição Cc/Cco, cabeçalhos e anexos Base64/CID conforme
  o DTO. Envio por modelo tem seu próprio formato, sem misturar campos exclusivos
  da composição direta. O cliente não baixa anexos remotos por iniciativa própria.
- Lotes seguem o array e a aceitação atômica do backend, sem dividir pedidos nem
  repetir automaticamente. Agendamento usa `agendada_em` ISO 8601 com fuso e as
  regras de estado do servidor. Aceitação não comprova entrega SMTP.
- Importações recebem CSV UTF-8 no corpo JSON. O limite de CSV é 8 MiB no contrato
  da API; o transporte admite JSON de até 50 MiB para acomodar escapes. Esse teto
  geral não amplia limites menores dos demais endpoints.
- Modelos, campanhas, automações e caixas preservam revisões, estados e campos
  anuláveis. Parar ou cancelar não desfaz efeitos já aceitos pelo servidor.
- A chave secreta de API só aparece na criação. Revogação pode retornar resposta
  vazia. Concessões CLI incluem consulta/revogação, sem iniciar autenticação
  interativa ou renovar tokens.

## Recebimento e fluxos

Original MIME, anexos recebidos e exportações usam rotas fixas autenticadas. URLs
temporárias presentes nos metadados são capacidades sensíveis; o SDK não as segue
automaticamente nem transfere a credencial para um destino informado pela API.
Retenção e disponibilidade do conteúdo são determinadas pelo servidor.

`baixar_original_fluxo`, `baixar_anexo_fluxo` e `baixar_fluxo` devolvem gestores de
contexto. Use `with` no cliente síncrono e `async with` no assíncrono; dentro do
contexto, consuma bytes por `for` ou `async for`. O leitor expõe `status`,
`cabecalhos` e `total_bytes`. O gestor assíncrono não recebe `await` antes de
`async with`. A saída do contexto fecha a resposta, inclusive no encerramento
antecipado do consumo.

O teto padrão de resposta é **16 MiB**, inclusive em fluxo e em respostas de erro;
`limite_resposta_bytes` permite ajustar a operação. O limite é aplicado durante a
leitura, não apenas depois de acumular o conteúdo.

## Transporte e limites

Cada cliente reutiliza seu pool HTTPX e deve ser fechado com contexto ou
`fechar()`; `ClienteAsync` usa fechamento aguardado e também oferece
`fechar_async()`. A comunicação padrão usa HTTPS verificado, recusa
redirecionamentos, não armazena cookies e não herda proxies do ambiente. Uma CA
privada pode ser configurada. HTTP é uma opção explícita restrita a loopback para
ensaios locais. Um transporte HTTP injetado tem sua política de rede sob controle
de quem o fornece.

O SDK solicita `Accept-Encoding: identity` e recusa codificações não negociadas.
Isso preserva os bytes de MIME, anexos e CSV e mantém o limite de leitura
previsível. Nenhuma falha produz repetição automática; preserve chave e conteúdo
ao decidir repetir uma intenção.

`tempo_limite`, por padrão **30 segundos**, limita a inatividade de cada etapa
HTTPX: pool, conexão, escrita ou leitura. A conexão usa no máximo o menor valor
entre esse limite e `tempo_conexao`, cujo padrão é **10 segundos**. **Não existe
um prazo total de relógio embutido**: um fluxo que continua avançando pode durar
mais. A aplicação assíncrona pode envolver a operação em `asyncio.timeout()` quando
precisar desse prazo total. Cancelar a espera não desfaz uma intenção aceita.

## Alcance da validação

A matriz do projeto é CPython **3.11–3.15**. Os exemplos opcionais exercitam Flask
e Django síncronos e FastAPI assíncrono; o exemplo Django é uma view direta, sem
implementar um backend de email. Veja [as integrações](integracoes.md) para as
versões e seus limites. SDK e frameworks têm contratos de compatibilidade distintos.

Os testes de contrato conferem as 151 operações de cada variante com um
transporte coletor. Ensaios HTTPS sintéticos verificam o transporte; o
[relatório de API local](integracao-api.json) registra a execução contra backend
isolado com dados sintéticos. Esses resultados não demonstram entrega SMTP,
produção, capacidade de escala ou deploy cloud.

Esta cobertura descreve a seleção implementada, não toda a API do produto.
Não inclui recursos globais de logs, uso ou supressões, autorização OAuth
interativa, helpers de sessão/dashboard nem renderização React. Campos adicionais
dos DTOs não implicam métodos ou fluxos novos no SDK.
