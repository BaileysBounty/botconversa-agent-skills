# Snapshot e diff

Capture estado suficiente para explicar, validar e reverter uma mudança. Trate respostas das tools como evidência; não confie em lembrança ou em resumo anterior.

## Três estados

Mantenha três representações separadas:

- **A — baseline original:** estado lido antes da proposta.
- **B — versão de teste:** estado efetivamente criado e relido, não apenas o payload enviado.
- **A' — original pré-promoção:** nova leitura imediatamente antes de escrever em produção.

Se A' divergir de A em qualquer dependência relevante, existe drift. Interrompa a promoção, mostre a divergência e recalcule a proposta.

## Conteúdo mínimo do snapshot

### Contexto

- data e hora da captura;
- companhia e nível de acesso de `get_connection_info`;
- objetivo e escopo aprovados;
- limitações de observabilidade.

### Flow

- `flow_id`, nome e pasta;
- starting block e destino exposto;
- lista dos GPT blocks;
- stubs de outros blocos visíveis nas conexões;
- conexões GPT→GPT, incluindo saída usada.
- campanhas, grupos de palavras-chave e steps de sequências que apontem para o flow, quando o inventário de entradas fizer parte do escopo.

### GPT block e assistant

Guardar IDs e valores completos disponíveis, incluindo:

- block ID, nome e posição;
- assistant ID, nome e `shared_with_block_ids`;
- `is_synced` e campos obrigatórios ausentes;
- modo de prompt e somente os campos do modo ativo;
- `is_starter_for_gpt`, `starter_message` e `error_message`, registrando se a abertura é orientação interna para a IA ou mensagem estática visível ao contato;
- modelo, idioma, versão, temperatura e tempos;
- outputs customizados e instruções;
- variáveis customizadas;
- skill IDs;
- MCP app IDs;
- calendários;
- conexões de sucesso, falha, inatividade e custom outputs.

### Skills

Para cada skill anexada, guardar:

- ID, nome e descrição;
- prompt completo;
- quais blocos conhecidos a utilizam, quando essa informação puder ser comprovada.

### Catálogos relevantes

Quando usados na mudança, guardar a opção escolhida e a evidência de que continua disponível/conectada para modelo, idioma, versão, MCP app e calendário.

## Normalização

- Diferenciar campo omitido, `null`, texto vazio e lista vazia; eles podem produzir efeitos diferentes.
- Comparar IDs como IDs, sem reconstruí-los pelo nome.
- Preservar a ordem quando ela tiver semântica; ordenar apenas coleções comprovadamente não ordenadas.
- Não copiar IDs internos de outputs ou variáveis antigas para objetos novos quando a tool permitir criá-los sem ID.
- Manter o payload bruto ou uma transcrição fiel junto do resumo humano.
- Não incluir tokens ou segredos em relatórios. Se uma resposta inesperada os contiver, redigir o valor.

## Diff proposto

Apresentar cada alteração em uma linha:

| Recurso | Campo | Antes | Depois | Motivo | Risco | Teste |
|---|---|---|---|---|---|---|
| GPT block 123 | `temperature` | 0,7 | 0,3 | reduzir variação em regra crítica | médio | T-08 |

Classificar a operação como:

- **adicionar:** não existia e passa a existir;
- **alterar:** valor muda;
- **remover/limpar:** valor será enviado como `null` ou lista vazia;
- **preservar:** campo relevante deliberadamente não muda.

Nunca esconder alteração de relacionamento dentro de “ajustes gerais”. Destacar separadamente `skill_ids`, `mcp_app_ids`, calendários, outputs e modo de prompt.

## Diff semântico de prompt

Além do texto integral antes/depois, resumir por regra:

| Regra | Ação | Razão | Comportamento esperado |
|---|---|---|---|
| confirmação de agenda | adicionada | evitar agendamento incorreto | confirmar data e fuso antes da ação |

Preservar fatos do negócio, proibições e condições não incluídas no escopo. Marcar qualquer exclusão, mesmo quando parecer redundante.

## Detecção de drift

Reler antes da promoção:

1. `get_connection_info`;
2. `list_gpt_blocks` do flow original;
3. `get_gpt_block` do alvo;
4. todas as skills originais ainda referenciadas ou consideradas no diff;
5. `list_gpt_assistant_options` se a mudança depender de app, calendário, modelo, idioma ou versão.

Considerar drift quando mudar:

- prompt, configuração ou relacionamentos do assistant;
- compartilhamento do assistant;
- conteúdo de skill relevante;
- destino exposto ou arquitetura GPT observável;
- disponibilidade/conexão de opção necessária;
- identidade do flow ou block alvo.

Não tentar mesclar silenciosamente. Mostrar `A → A'`, atualizar o baseline e solicitar nova aprovação do diff recalculado.

## Read-after-write

Depois de cada escrita:

- usar a tool de leitura mais específica;
- comparar a resposta lida ao payload aprovado;
- conferir `is_synced`, campos obrigatórios e compartilhamento;
- confirmar que listas não foram limpas por engano;
- registrar IDs realmente criados;
- tratar resposta de sucesso sem estado correspondente como falha de verificação.

O estado B ou final é o que foi relido, não o que a operação declarou que faria.
