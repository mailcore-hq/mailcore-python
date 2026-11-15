# Verificação do cliente Python

O laboratório usa dados sintéticos. Não publica pacotes, não faz deploy nem envia
SMTP. Os relatórios JSON registram versões, imagens e resultados observados.

Em 14/11/2026, passaram **439 testes por versão** em CPython 3.11.18, 3.12.16,
3.13.18, 3.14.10 e 3.15.2, sem falhas, erros ou testes ignorados. Também passaram
os verificadores de estilo/tipos e a instalação offline da wheel nos cinco perfis.

## Matriz e pacote

```sh
sh scripts/verificar.sh
```

O host precisa apenas de shell POSIX e Docker Linux acessível ao usuário.
Python, pip, ferramentas de qualidade e frameworks rodam dentro das imagens.
As cinco bases Python 3.11–3.15 estão fixadas por digest, e as dependências por
`requirements-testes-py311.txt` e `requirements-testes-modern.txt`.
Django usa 5.2 LTS em Python 3.11 e 6.1 nos demais perfis; Flask e FastAPI são
exercitados nas mesmas versões travadas em ambas as listas.

Os relatórios `python-*.json` devem apresentar `resultado: "aprovado"`, sem erros,
falhas ou testes ignorados. A suíte inclui contratos das 151 operações em cada
variante, TLS real, identificação por idempotência, isolamento de threads/tasks,
pooling HTTP/1.1, limites, erros, respostas truncadas, MIME/CSV binários,
cancelamento e liberações de conexão. Os exemplos usam os clientes de teste reais
de Flask/FastAPI/Django e um SDK sintético no limite de envio.

Ruff, mypy estrito, exemplos de consumo dos tipos e o gerador de fontes também
são conferidos. As fontes são estáticas: não há geração de métodos ao importar o
pacote. O marcador `py.typed` é distribuído com a wheel.

O processo constrói sdist e wheel a partir dele, prepara as dependências de
runtime e instala a wheel offline em cinco containers Python mínimos. A prova
de instalação usa somente o pacote instalado, sem checkout no caminho de importação
e sem carregar frameworks. SHA-256 acompanha os dois arquivos próprios em `dist/`.
As wheels de dependências ficam separadas em `dist/dependencias` para esse ensaio;
não são incorporadas ao pacote Mailcore.

## API e PostgreSQL reais locais

```sh
sh scripts/verificar_api.sh
```

Esse ensaio adicional precisa do checkout backend, runtime local da API, imagem
Rust e cache público Cargo já preparados. Ele compila com `--offline --locked`
em Docker e registra revisão e SHA-256 dos fontes/binário. Use `MAILCORE_BACKEND`
para outro checkout e `MAILCORE_IMAGEM_CLIENTE` para outra imagem do SDK. As
opções do controlador podem ser consultadas com `python testes/controlar_api.py
--help` dentro da imagem. Nenhuma ferramenta é instalada no host.

O [relatório aprovado](integracao-api.json) registra 12 grupos, 23 migrações,
HTTPS verificado e PostgreSQL com TLS `verify-full`. O ambiente é exclusivo, em
rede Docker interna, sem portas publicadas, worker, Postal ou SMTP. Configuração,
chaves e certificados são sintéticos e vivem em volume temporário de memória.

Foram exercitados permissões Full/Sending, composição/CID/Cc/Cco, replay/conflito,
lote atômico, domínios, contatos/catálogos/exportação CSV em fluxo,
modelos/pastas/versões/publicação com revisão, marketing sem disparo,
caixas/etiquetas/rascunhos, recebimento MIME real, concessões CLI e revogação.
O replay async não cria outra intenção; o download MIME async mantém os bytes.
Um callback privado sintético assinado registra o recebimento sem iniciar Postal.
O banco terminou com três mensagens/três tarefas de envio e um recebido pendente.

A [interrupção SIGTERM](integracao-api-interrupcao.json) também foi conferida:
falha intencional, limpeza concluída e nenhum recurso rotulado restante.
Credenciais e corpos não entram nos relatórios. `resultado: "aprovado"` e
`limpeza_concluida: true` são necessários para aprovar uma execução normal.

## Limites

Os prazos seguem HTTPX: inatividade por etapa, sem promessa de limite total de
relógio. A suíte confirma essa distinção com resposta em partes que permanece
ativa. `asyncio.timeout()` do chamador pode impor prazo total e a biblioteca
propaga cancelamento, fechando o stream.

Os testes não comprovam entrega SMTP, configuração cloud, todas as versões de
frameworks, outros interpretadores ou desempenho em produção. Uma implantação
posterior requer sua própria validação de produção. Nenhum pacote foi publicado.
