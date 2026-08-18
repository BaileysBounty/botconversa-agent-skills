---
name: botconversa-company-checkup
description: Audita, somente em leitura, a configuração visível de uma companhia BotConversa e prioriza riscos, inconsistências e oportunidades. Use quando pedirem check-up, diagnóstico, auditoria ou sugestões para uma conta existente, incluindo flows, agentes GPT, skills, campos, tags, campanhas, Kanban, palavras-chave, sequências e configurações de atendimento.
---

# Check-up da companhia BotConversa

Produzir um diagnóstico baseado apenas no que o MCP comprova. Separar configuração observável, hipótese e área não verificável; nunca alterar a companhia.

## Guardrails obrigatórios

- Começar sempre por `get_connection_info`. Interromper o check-up se a conexão BotConversa não estiver disponível ou a companhia não puder ser identificada.
- Usar exclusivamente as operações de leitura da allowlist em [capacidades.md](references/capacidades.md). Não criar, atualizar, mover, duplicar, conectar ou excluir recursos, mesmo que pareça seguro.
- Não tratar ausência, nomenclatura ou falta de referência visível como prova de falta de uso. Dizer “não referenciado no escopo exposto”, nunca “não utilizado”, salvo se uma métrica explícita comprovar isso.
- Tratar a análise de flows como parcial: o MCP detalha blocos GPT, mas outros blocos aparecem apenas como stubs de conexão. Não afirmar que revisou mensagens, menus, condições, ações ou a jornada ponta a ponta.
- Não inventar métricas, período, intenção, impacto ou contexto de negócio. Identificar claramente o que é confirmado, inferido e não verificável conforme [modelo-de-evidencia.md](references/modelo-de-evidencia.md).
- Não aplicar sugestões nesta skill. Quando pedirem execução no mesmo pedido, concluir o diagnóstico e apresentar mudanças propostas como pendentes de aprovação; para agentes GPT, indicar a skill `botconversa-agent-upgrade`.

## Executar o check-up

1. **Confirmar a conexão.** Chamar `get_connection_info`; registrar companhia, usuário autenticado e nível de acesso. A skill continua read-only mesmo quando o acesso concedido for `write`.
2. **Montar o inventário.** Ler [inventario-paginado.md](references/inventario-paginado.md) e percorrer todas as páginas, detalhes e relacionamentos expostos. Manter um ledger de cobertura por domínio.
3. **Correlacionar configurações.** Relacionar flows com campanhas, grupos de palavras-chave e passos de sequência; agentes GPT com skills, apps MCP, calendários e campos; boards com colunas e regras. Comparar capacidades prometidas pelo prompt com integrações observáveis e com as proteções comportamentais do agente, sem presumir permissões granulares do runtime.
4. **Avaliar evidências.** Ler [regras-de-checkup.md](references/regras-de-checkup.md), aplicar primeiro verificações determinísticas e só depois hipóteses contextuais. Não transformar oportunidade genérica em problema.
5. **Priorizar.** Ordenar por severidade, força da evidência, abrangência e esforço de validação. Entregar até três recomendações principais; entregar menos quando não houver três conclusões defensáveis.
6. **Reportar.** Seguir integralmente [contrato-do-relatorio.md](references/contrato-do-relatorio.md). Citar tool, recurso e campos que sustentam cada achado; omitir segredos e prompts completos desnecessários.

## Lidar com cobertura incompleta

- Repetir uma chamada de leitura que falhar uma vez quando o erro parecer transitório.
- Se a falha persistir, marcar o domínio como `Parcial` ou `Indisponível`, registrar a chamada que falhou e continuar nos demais domínios.
- Se limites de tempo ou volume impedirem o inventário completo, não extrapolar a amostra. Informar páginas, recursos e detalhes efetivamente inspecionados.
- Quando um app MCP estiver anexado, registrar somente a presença da relação e as opções expostas. O connector não prova, por si só, quais tools o agente receberá por contato nem se um efeito externo será concluído.
- Encerrar com “estável no escopo visível”, e não “companhia saudável”, quando não houver achados críticos.

## Referências

- [capacidades.md](references/capacidades.md): allowlist, cobertura atual e limites do MCP.
- [inventario-paginado.md](references/inventario-paginado.md): ordem das chamadas e critério de completude.
- [modelo-de-evidencia.md](references/modelo-de-evidencia.md): classes de evidência e linguagem permitida.
- [regras-de-checkup.md](references/regras-de-checkup.md): verificações e prioridades.
- [contrato-do-relatorio.md](references/contrato-do-relatorio.md): estrutura obrigatória da entrega.
