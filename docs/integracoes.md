# Exemplos Flask, FastAPI e Django

Os três exemplos usam o mesmo SDK Python e oferecem `POST /enviar` para aceitar
uma intenção de envio com remetente, destinatário e conteúdo fixos. Cada fábrica
recebe sua configuração no boot. Parâmetros HTTP, JSON e query não configuram o
cliente nem transformam a rota em um relay livre de email.

| Exemplo                   | Entrada                                   | Cliente do SDK                        |
| ------------------------- | ----------------------------------------- | ------------------------------------- |
| `exemplos/flask_app.py`   | Fábrica `criar_aplicacao` para WSGI       | `Cliente`, síncrono                   |
| `exemplos/fastapi_app.py` | Fábrica `criar_aplicacao` para ASGI       | `ClienteAsync`, aguardado com `await` |
| `exemplos/django_app.py`  | Fábrica `criar_view` para uma rota Django | `Cliente`, síncrono                   |

Os frameworks são dependências opcionais dos exemplos e dos testes. Importar
`mailcore` não carrega Flask, FastAPI ou Django.

## Configuração

Forneça estas variáveis pelo mecanismo de segredos da aplicação em Docker:

| Variável                | Uso                                                          |
| ----------------------- | ------------------------------------------------------------ |
| `MAILCORE_API_KEY`      | Credencial do SDK para a API                                 |
| `TOKEN_APLICACAO`       | Credencial independente para autorizar a rota demonstrativa  |
| `MAILCORE_REMETENTE`    | Remetente fixo em domínio autorizado                         |
| `MAILCORE_DESTINATARIO` | Destinatário fixo                                            |
| `MAILCORE_API_URL`      | Opcional: URL base HTTPS; quando ausente usa o padrão do SDK |

Gere o token com 32 bytes aleatórios, por exemplo `secrets.token_urlsafe(32)`.
O exemplo aceita sua representação Base64URL de 43 a 256 caracteres, usando
letras, números, `_` e `-`. O token deve ser diferente da chave da API. A
configuração inválida falha no boot, antes de abrir a rota. A autenticação compara
resumos SHA256 de tamanho fixo com `hmac.compare_digest`.

As fábricas aceitam `ambiente=` com um Mapping e `cliente=` com uma instância
isolada. Esses argumentos só existem no código de inicialização. São úteis para
configurar organizações separadamente e testar sem credenciais reais. Não troque
clientes globais durante pedidos concorrentes.

## Carregar na aplicação

Flask:

```python
from exemplos.flask_app import criar_aplicacao

aplicacao = criar_aplicacao()
```

FastAPI:

```python
from exemplos.fastapi_app import criar_aplicacao

aplicacao = criar_aplicacao()
```

Carregue a aplicação pelo servidor WSGI ou ASGI do seu ambiente Docker. O exemplo
FastAPI usa o lifespan para criar e fechar seu cliente no mesmo contexto; não
habilita páginas de documentação nem rotas OpenAPI. Ele usa I/O assíncrono do SDK
e não bloqueia a rota com o cliente síncrono.

Para Django, configure os limites da aplicação dedicada ao exemplo:

```python
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 4096
```

Depois, registre a view:

```python
from django.urls import path
from exemplos.django_app import criar_view

urlpatterns = [path("enviar", criar_view())]
```

O exemplo Django usa uma view HTTP que chama o SDK diretamente. Ele não implementa
um backend de `django.core.mail`. Adaptadores externos dessa API têm contrato e
validação próprios. Esta view dispensa CSRF somente nessa rota de máquina,
autenticada pelo Bearer obrigatório; ela não usa sessão ou cookie para autorizar o
envio. As demais rotas da aplicação preservam sua configuração de CSRF.

Os clientes criados pelas fábricas são reutilizados. Flask e Django registram seu
fechamento no término normal do processo; FastAPI fecha no encerramento do
lifespan. Quando uma instância é injetada, quem a criou é responsável por fechá-la.

## Fazer uma chamada

```sh
curl --request POST "$URL_APLICACAO/enviar" \
  --header "Authorization: Bearer $TOKEN_APLICACAO" \
  --header 'Idempotency-Key: pedido-123-confirmacao' \
  --header 'Content-Type: application/json' \
  --data '{}'
```

O corpo deve ser um objeto JSON válido em UTF-8, com até 4 KiB. Seus campos são
ignorados pelo envio fixo. A chave de idempotência é obrigatória: de 1 a 256
caracteres ASCII visíveis, sem vírgulas. Preserve a chave para repetir
explicitamente a mesma intenção de negócio. O SDK e os exemplos não repetem o
envio automaticamente após uma falha ambígua.

Os exemplos retornam `202` com apenas `id` e `estado` depois da aceitação. Isso não
comprova entrega SMTP. Autenticação inválida retorna `401`; chave ou JSON inválido,
`400`; corpo acima do limite, `413`; tipo de conteúdo diferente de JSON, `415`.
Métodos não previstos recebem `405`. Erros da API preservam um status HTTP de erro
aplicável, com mensagem genérica. Transporte, redirecionamento recusado ou resposta
incompleta resultam em `502`, sem expor chave, cabeçalhos privados ou detalhes da
exceção.

Flask usa `MAX_CONTENT_LENGTH` e leitura limitada. FastAPI consome o stream ASGI
até o limite antes de interpretar JSON; não declara um parâmetro de corpo para
pré-processamento pelo Pydantic. Django verifica o tamanho e lê no máximo 4 KiB
mais um byte, além da configuração de limite do framework. Configure também os
limites e prazos do servidor HTTP e do proxy da sua aplicação.

## Compatibilidade e testes

Os pinos de framework avaliados são Flask `3.1.3`, FastAPI `0.162.7` e Django
`6.1.3`. Django `6.1.3` suporta Python 3.12–3.15. Para Python 3.11, os testes usam
Django `5.2.19` LTS. A compatibilidade do SDK é documentada separadamente no
relatório geral; ela não implica suporte a todas as versões dos frameworks.

`testes/testes_exemplos.py` usa clientes de teste Flask e Django e o transporte
ASGI do HTTPX contra FastAPI reais. O ponto de I/O do SDK é substituído por um
cliente sintético injetado no boot. Os cenários exercitam roteamento, CSRF do
endpoint de máquina, credenciais, JSON/UTF-8, tamanho, corpo malicioso,
idempotência repassada, falhas sanitizadas e fechamento do cliente assíncrono.

A execução local em Python 3.12 concluiu dez testes sem falhas. Um stream virtual
ASGI de 1 GiB, sem Content-Length, foi interrompido após cinco partes de 1 KiB,
sem ler o restante ou chamar o SDK. O ensaio usa uma sequência gerada sob demanda,
sem alocar 1 GiB de dados.

Esses testes não abrem portas, chamam uma API externa ou enviam SMTP. Repetir a
mesma chave no teste confirma sua preservação pelo exemplo; a deduplicação na API
real depende do servidor. Use o verificador Docker do projeto para executar a
matriz, sem instalar Python ou dependências no host.

Documentação dos componentes:
[Flask](https://flask.palletsprojects.com/en/stable/),
[FastAPI](https://fastapi.tiangolo.com/advanced/async-tests/) e
[Django](https://docs.djangoproject.com/en/6.1/topics/testing/tools/).
