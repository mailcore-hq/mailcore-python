# Mailcore para Python

[Código-fonte](https://github.com/mailcore-hq/mailcore-python) · [Problemas e sugestões](https://github.com/mailcore-hq/mailcore-python/issues)

Cliente Python da API Mailcore, em versão alpha `0.2.0a1`. O pacote de
distribuição é `mailcore-sdk` e o módulo importado é `mailcore`.
Requer Python 3.11 ou superior.

## Instalação

Na aplicação consumidora:

```sh
python -m pip install 'mailcore-sdk==0.2.0a1'
```

## Primeiro envio

```python
import os
from mailcore import Cliente, PedidoEmail

pedido: PedidoEmail = {
    "remetente": "Equipe <equipe@example.com>",
    "destinatarios": ["pessoa@example.com"],
    "assunto": "Bem-vindo",
    "html": "<p>Sua conta está pronta.</p>",
}
with Cliente(chave_api=os.environ["MAILCORE_API_KEY"]) as cliente:
    resposta = cliente.emails.enviar(pedido, chave_idempotencia="pedido-123-confirmacao")
    print(resposta["id"])
```

Use a chave somente no servidor, com remetente de domínio verificado. A aceitação
da intenção não comprova entrega SMTP. Preserve chave e conteúdo ao repetir uma
intenção; o SDK não faz tentativas automáticas após erro ou timeout.

## Cliente assíncrono

```python
from mailcore import ClienteAsync, PedidoEmail

async def enviar(pedido: PedidoEmail) -> str:
    async with ClienteAsync() as cliente:
        resposta = await cliente.emails.enviar(pedido, chave_idempotencia="pedido-123-confirmacao")
        return resposta.dados["id"]
```

Os dois clientes oferecem os mesmos recursos. As chamadas async usam HTTPX
assíncrono nativo. Reutilize o cliente durante a vida da aplicação; `with`,
`async with` ou `fechar()` liberam os pools. Não compartilhe um cliente async
entre event loops. A chave pode ser uma função sem argumentos, resolvida por
operação, para permitir rotação sem alterar um estado global.
Um fornecedor que retorne uma chave inválida falha; não usa outra chave do ambiente.
O pool padrão permite até 100 conexões e 20 ociosas, configuráveis por
`maximo_conexoes` e `conexoes_ociosas`.

## Respostas e erros

`Resposta.dados` preserva os campos e envelopes JSON da API. `status` e
`cabecalhos` expõem metadados HTTP, e `resposta["id"]` abrevia o acesso ao JSON.
Bytes de downloads são `bytes`; prévias HTML são `str`. `ErroApi` preserva código
e status da rejeição; `ErroTransporte` trata rede/prazo; `ErroResposta` trata
conteúdo inválido ou excedido; `ErroConfiguracao` trata opções inválidas.

O cliente exige TLS verificado, não segue redirecionamentos, não armazena cookies
e não herda proxies do ambiente. Uma CA privada pode ser informada por
`certificado_ca`. Somente loopback pode usar HTTP com `permitir_http_local=True`.
`transporte_http` permite um adaptador HTTPX explicitamente fornecido pela aplicação;
esse adaptador e sua política de rede são responsabilidade de quem o configura.

`tempo_limite` (30 segundos por padrão) segue a semântica HTTPX: limite de
inatividade de cada etapa de conexão, pool, escrita ou leitura. **Não é um prazo
total de relógio**. A conexão tem limite adicional de 10 segundos. Uma aplicação
async que precise de prazo total pode envolver a operação em `asyncio.timeout()`;
o cancelamento é propagado e a resposta é fechada. Um prazo vencido não desfaz
uma intenção já aceita.

A resposta tem teto padrão de 16 MiB, inclusive em fluxo, ajustável por operação
com `limite_resposta_bytes`. O JSON de pedido admite até 50 MiB para o envelope de
importação CSV; os limites específicos de cada DTO pertencem à API. A comunicação
solicita `Accept-Encoding: identity` e recusa codificações não negociadas.

## Downloads e webhooks

```python
with Cliente() as cliente:
    with cliente.recebimento.baixar_original_fluxo("id-da-mensagem") as fluxo:
        with open("mensagem.eml.parcial", "wb") as arquivo:
            for parte in fluxo:
                arquivo.write(parte)
```

No cliente async, use `async with` e `async for`. Os fluxos preservam bytes MIME,
exigem consumo dentro do contexto e liberam a conexão ao terminar, interromper
ou cancelar. Só trate arquivos parciais como completos depois de sucesso.
Downloads usam rotas autenticadas; URLs temporárias de metadados não são acessadas
automaticamente.

Para encaminhar um recebido completo com novos remetente e destinatários:

```python
from mailcore import Cliente, PedidoEncaminhamentoRecebido

pedido: PedidoEncaminhamentoRecebido = {
    "recebido_id": "id-do-recebido",
    "remetente": "Equipe <avisos@seudominio.com.br>",
    "destinatarios": ["pessoa@exemplo.com.br"],
}
with Cliente() as cliente:
    resposta = cliente.recebimento.encaminhar(pedido, chave_idempotencia="encaminhamento-123")
```

O modo padrão conserva assunto, texto, HTML CID e todos os anexos do detalhe.
Para anexar o original como EML, acrescente `preservar_conteudo=False` e informe
`texto` e/ou `html` no pedido. Nesse modo o assunto recebe `Fwd:` uma única vez.
O cliente async usa `await cliente.recebimento.encaminhar(pedido, **opcoes)`.
O retorno é `Resposta[RespostaEnvio]`, com o ID da nova mensagem.

O helper requer conteúdo disponível e processamento concluído; valida todos os
metadados antes de baixar e confere os bytes reais. Aceita até dez anexos somando
5 MiB, corpo de até 500 KiB, JSON de até 8 MiB e cinquenta destinatários. Um tipo
proibido ou arquivo ausente encerra a operação inteira. Downloads são sequenciais,
em memória e somente por rotas autenticadas. A chave de idempotência vai apenas
no POST final, sem repetição automática. Permissões de leitura e envio devem
pertencer à mesma credencial. Consulte [a cobertura](docs/cobertura.md).

`verificar_assinatura(corpo_bruto, cabecalhos, segredo)` verifica HMAC-SHA256
`svix-*`, com comparação em tempo constante e janela de cinco minutos. Passe o
corpo bruto antes de interpretar JSON. Deduplicação e confirmação durável dos
eventos pertencem ao consumidor.

## Documentação e desenvolvimento

Consulte [cobertura](docs/cobertura.md), [integrações Flask/FastAPI/Django](docs/integracoes.md)
e [verificação](docs/verificacao.md). Não há dependência de framework no runtime
do pacote.

Para desenvolver com o checkout local, use `python -m pip install -e .`.
Uma instalação a partir dos artefatos gerados usa a wheel local:

```sh
python -m pip install /caminho/mailcore_sdk-0.2.0a1-py3-none-any.whl
```

O pip resolve as dependências declaradas; o arquivo do SDK é local nessa
modalidade. O `.tar.gz` de `dist/` também pode ser instalado pelas ferramentas
Python habituais. Para verificar o projeto:

```sh
sh scripts/verificar.sh
```

O desenvolvimento e os testes usam Docker, sem instalar Python, pip ou frameworks
no host. O script de verificação não publica pacotes nem faz deploy.
A publicação usa o workflow manual `Publicar no PyPI`, separado dessas verificações.
