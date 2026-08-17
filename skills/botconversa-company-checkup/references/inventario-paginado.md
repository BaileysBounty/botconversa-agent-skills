# Workflow de inventário paginado

## Ordem de coleta

1. Chamar `get_connection_info`. Parar se a conexão ou a companhia não forem confirmadas.
2. Chamar `get_company_settings` e `list_gpt_assistant_options` uma vez.
3. Chamar `list_folders` e achatar a árvore preservando `id`, nome, pai e caminho completo.
4. Paginar `list_flows`. Para cada flow, chamar `list_gpt_blocks`; para cada bloco GPT retornado, chamar `get_gpt_block`.
5. Paginar `list_skills`; chamar `get_skill` para cada skill.
6. Paginar `list_user_fields`, `list_bot_fields`, `list_tags` e `list_campaigns`.
7. Paginar `list_boards`; chamar `get_board` para cada board.
8. Paginar `list_keyword_groups`.
9. Paginar `list_sequences`; chamar `get_sequence` para cada sequência.
10. Paginar `list_fast_replies`; chamar `list_chat_close_reasons` e `get_scheduled_send_presets` uma vez.

Use filtros vazios para o inventário completo. Filtros de busca servem apenas para uma análise explicitamente limitada pelo usuário.

## Algoritmo de paginação

Para cada operação paginada:

1. Inicializar `page=1` e `page_size=30`.
2. Acrescentar os itens recebidos ao inventário, deduplicando pelo ID; quando não houver ID, usar a chave natural retornada e registrar essa limitação.
3. Tratar a indicação explícita de paginação como fonte principal:
   - encerrar quando `next` for `null`;
   - ou quando `has_next`/`has_more` for `false`;
   - ou quando `page` alcançar o total de páginas informado.
4. Se não houver metadata de término, continuar enquanto a página tiver 30 itens e encerrar após a primeira página vazia ou com menos de 30.
5. Incrementar a página sem alterar filtros ou tamanho.
6. Detectar repetição da mesma página ou cursor. Interromper e marcar o domínio como `Parcial`, em vez de entrar em loop.

Não declarar inventário completo com base apenas na primeira página. Uma lista vazia só comprova ausência quando a chamada terminou normalmente e a paginação foi encerrada.

## Detalhes dependentes

Complete as chamadas filhas antes de classificar o domínio:

| Lista | Detalhe obrigatório | Completude |
|---|---|---|
| `list_flows` | `list_gpt_blocks` por flow e `get_gpt_block` por bloco GPT | Ainda `Parcial` pelo limite estrutural de flows |
| `list_skills` | `get_skill` por skill | `Completo` no escopo exposto quando todos retornarem |
| `list_boards` | `get_board` por board | `Completo` para estrutura, sem cards |
| `list_sequences` | `get_sequence` por sequência | `Completo` para configuração, sem membros |

Processar detalhes em lotes pequenos quando houver muitos recursos. Uma falha individual não deve eliminar os resultados já confirmados.

## Ledger de cobertura

Manter internamente uma linha por domínio:

```text
domínio | páginas concluídas | itens listados | detalhes esperados/concluídos | falhas | status
```

Usar somente estes status:

- `Completo`: todas as páginas e detalhes expostos foram lidos.
- `Parcial`: houve falha, interrupção, limite estrutural ou amostragem.
- `Indisponível`: não existe tool atual para o domínio.

Flows são sempre `Parcial`. Boards podem ser `Completo para estrutura; cards indisponíveis`. Atendimento pode ser `Completo para configurações; operação indisponível`.

## Normalização para correlações

- Preservar IDs como identidade principal; nomes são apenas apresentação.
- Manter referências de flow originadas em campanhas, keywords e passos de sequência.
- Manter relação `assistant_id -> block_ids` e `skill_id -> block_ids`.
- Comparar nomes somente após remover espaços externos e normalizar caixa; conservar o original no relatório.
- Não converter “não referenciado nas áreas expostas” em “sem uso”.
