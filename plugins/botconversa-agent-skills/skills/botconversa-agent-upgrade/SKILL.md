---
name: botconversa-agent-upgrade
description: Revisar, melhorar e versionar com segurança agentes GPT do BotConversa usando o MCP. Usar quando alguém pedir para avaliar um agente, melhorar prompt ou skills, preparar uma v2 isolada, comparar versões, criar uma bateria de testes ou promover alterações aprovadas ao fluxo original sem interromper a produção.
---

# Melhorar agentes do BotConversa

## Objetivo

Produzir uma revisão baseada em evidências, preparar uma versão separada para testes e somente promover alterações ao agente original depois de testes e aprovação explícita. Preservar o original e manter uma trilha clara de snapshot, diff, consentimento e verificação.

## Carregar as referências

- Ler [rubrica-do-agente.md](references/rubrica-do-agente.md) antes de pontuar ou recomendar mudanças.
- Ler [snapshot-e-diff.md](references/snapshot-e-diff.md) ao capturar estado, comparar versões ou verificar drift.
- Ler [isolamento-seguro.md](references/isolamento-seguro.md) antes de qualquer criação ou alteração no BotConversa.
- Ler [bateria-de-testes.md](references/bateria-de-testes.md) ao preparar ou avaliar a validação da v2.
- Ler [promocao.md](references/promocao.md) integralmente antes de tocar o agente original.

## Invariantes de segurança

1. Chamar `get_connection_info` primeiro. Com acesso `read`, limitar o trabalho à análise e ao plano.
2. Tratar revisão, criação da v2 e promoção como etapas distintas. Exigir autorização explícita e delimitada antes de cada etapa com escrita; uma autorização para criar a v2 nunca autoriza alterar produção.
3. Nunca editar ou excluir o agente original durante a análise ou construção da v2.
4. Nunca ligar o fluxo de teste a campanha, palavra-chave, sequência ou outro ponto de entrada de produção.
5. Não assumir que `duplicate_flow` cria um assistant independente. Verificar `shared_with_block_ids` antes de alterar qualquer GPT duplicado.
6. Criar novas skills do BotConversa para todo conteúdo de skill alterado; não sobrescrever silenciosamente uma skill compartilhada.
7. Nunca usar `apply_to_all_blocks=true` sem mapear o blast radius e obter consentimento explícito para todos os blocos e fluxos afetados.
8. Revalidar o estado imediatamente antes da promoção e reler tudo que foi escrito. Interromper se houver drift ou readback divergente.
9. Separar claramente fatos observados, inferências e itens não verificáveis. Não alegar que conversas, desempenho ou blocos não GPT foram testados quando as tools não oferecem essa evidência.
10. Não apagar automaticamente o fluxo de teste, skills clonadas ou snapshots. Mantê-los como referência de rollback até o usuário decidir o descarte.
11. Tratar skills como conhecimento operacional, não como permissões. Preservar todas as tools disponibilizadas pelo app MCP e não criar allowlists artificiais por módulo.
12. Respeitar a fronteira determinística do runtime: toda ação sobre subscriber ou card afeta o contato atual da conversa, nunca outro contato citado na mensagem.
13. Não assumir que um flow de teste transforma calendários ou sistemas externos em sandbox. Usar destinos externos de teste e confirmar ações sensíveis quando necessário.

## Fluxo de trabalho

### 1. Resolver o alvo e o escopo

- Confirmar companhia, nível de acesso, fluxo e GPT block exatos.
- Usar `list_flows`, `list_gpt_blocks` e `get_gpt_block`; nunca escolher por semelhança de nome quando houver ambiguidade.
- Explicar que outros tipos de bloco aparecem apenas como stubs e não permitem uma auditoria integral do flow.
- Definir se o pedido abrange somente prompt, também skills, configuração do assistant, saídas ou arquitetura GPT→GPT.

### 2. Capturar o baseline

- Registrar um snapshot completo do original seguindo [snapshot-e-diff.md](references/snapshot-e-diff.md).
- Buscar o conteúdo de cada skill anexada com `list_skills` e `get_skill`.
- Consultar `list_gpt_assistant_options` quando modelo, idioma, versão, MCP apps ou calendário fizerem parte da revisão.
- Capturar `shared_with_block_ids`, `is_synced`, campos obrigatórios ausentes, conexões e modo de prompt.

### 3. Avaliar e propor

- Aplicar a rubrica somente ao que for observável.
- Priorizar falhas confirmadas, riscos confirmados, inconsistências prováveis e oportunidades.
- Quando a proposta acrescentar CRM do contato, handoff, Kanban, agenda, flows, sequências ou integrações, selecionar política-base e módulos com a skill `botconversa-runtime-pack` em vez de espalhar instruções operacionais duplicadas.
- Entregar o diagnóstico, o diff proposto e as limitações antes de escrever.
- Mostrar exatamente quais recursos seriam criados. Aceitar como autorização da v2 apenas um pedido explícito e delimitado, como “crie essa v2”; nunca inferir autorização de produção.

### 4. Construir a v2 isolada

- Confirmar novamente `access=write` imediatamente antes da primeira criação. Se a conexão ou o acesso tiver mudado, parar e reapresentar o plano.
- Preferir `create_gpt_flow` para um agente simples iniciado diretamente por GPT.
- Usar `duplicate_flow` somente como cópia para inspeção quando for necessário preservar uma estrutura mais complexa. Não executar ou chamar essa cópia de segura até a revisão manual obrigatória de todos os blocos não GPT.
- Clonar cada skill que receber alterações e anexar os novos IDs à v2.
- Manter no prompt principal as regras permanentes de privacidade, escopo do contato atual, confirmação proporcional, prevenção de duplicidade, falha segura e handoff. Skills runtime especializam domínios sem restringir as tools disponíveis.
- Anexar o app MCP confirmado para que a v2 preserve a superfície completa de capacidades do agente.
- Nomear recursos de modo inequívoco, por exemplo `[TESTE] Qualificação — v2`.
- Reler flow, GPT block, assistant e skills criados; registrar os IDs e o estado de sincronização.
- Verificar campanhas, grupos de palavras-chave e steps de sequências antes de afirmar que a v2 não possui entrada de produção.

### 5. Preparar e acompanhar os testes

- Montar a bateria proporcional ao comportamento alterado.
- Deixar explícito que o MCP atual não executa o simulador nem lê a conversa de teste; solicitar evidências manuais.
- Testar mutações internas com um contato de teste. Antes de testar qualquer efeito externo, confirmar contas, calendários, destinos e dados inequivocamente destinados a teste. Se isso não puder ser comprovado, testar apenas leitura, decisão e pedido de confirmação.
- Não marcar um caso como aprovado sem saída observada. Registrar falhas, desvios aceitos e itens não executados.

### 6. Promover somente após validação

- Apresentar resultados, diff exato de produção, blast radius e plano de rollback.
- Obter uma nova aprovação explícita para o bloco e os campos indicados.
- Executar o protocolo de drift, escrita mínima e read-after-write de [promocao.md](references/promocao.md).
- Encerrar com o estado final observado, as limitações restantes e a localização da v2 mantida para rollback.

## Contrato de saída

Organizar cada entrega com:

1. **Alvo e escopo:** companhia, flow, block e IDs confirmados.
2. **Estado atual:** fatos observados e limitações de visibilidade.
3. **Diagnóstico:** severidade, evidência, impacto e recomendação.
4. **Versão proposta:** diff por campo, skills clonadas e itens preservados.
5. **Segurança:** isolamento, compartilhamentos, blast radius e aprovações.
6. **Validação:** bateria, evidências e resultado por caso.
7. **Próxima decisão:** criar v2, corrigir a v2, promover ou manter sem alteração.
