# Contrato do relatório

Entregar o relatório em português, direto e acionável. Não executar nenhuma alteração.

## 1. Resumo executivo

Começar com o resultado, não com a lista de chamadas realizadas.

```text
Situação no escopo visível: Crítica | Requer atenção | Estável
Companhia: nome e ID
Cobertura: X domínios completos, Y parciais, Z indisponíveis
Síntese: uma frase com o achado mais importante
```

Usar:

- `Crítica` quando existir P0 confirmado;
- `Requer atenção` quando existir P1 e nenhum P0;
- `Estável no escopo visível` quando não houver P0/P1.

Não atribuir nota numérica arbitrária e não declarar a companhia saudável como um todo.

## 2. Recomendações principais

Entregar até três itens, em ordem de prioridade. Para cada item:

```text
Título
Prioridade e classificação
O que foi observado
Evidência: tool + recurso/ID + campos relevantes
Por que importa
Sugestão
Como validar antes de alterar produção
```

Manter separada qualquer hipótese. Não incluir uma recomendação fraca apenas para completar três itens.

## 3. Cobertura da análise

Usar uma tabela:

| Domínio | Status | Inspecionado | Limitação |
|---|---|---:|---|

Mostrar páginas, itens e detalhes concluídos quando relevante. Flows devem aparecer como `Parcial` mesmo quando todos os blocos GPT forem lidos. Para boards e atendimento, distinguir estrutura/configuração de operação real.

## 4. Diagnóstico detalhado

Agrupar por prioridade: P0, P1, P2 e P3. Omitir grupos vazios. Usar o formato do modelo de evidência e evitar repetir as recomendações principais palavra por palavra.

Para inconsistências semânticas, citar somente o menor trecho necessário do prompt. Nunca reproduzir prompts completos por conveniência.

## 5. Oportunidades condicionais

Separar ideias que dependem do contexto do negócio. Para cada uma, informar:

- sinal observado;
- benefício esperado como hipótese;
- pergunta que precisa ser respondida;
- pequena experiência ou validação sugerida.

Exemplo aceitável: “Não há board configurado. Como os nomes X e Y sugerem qualificação e handoff, um board pode tornar as etapas visíveis; confirme se essa passagem ocorre hoje no atendimento.”

Exemplo proibido: “Sua operação precisa de um Kanban.”

## 6. O que não foi possível verificar

Listar apenas limitações relevantes para as conclusões, como conversas, subscribers, cards, performance de operadores, conteúdo não GPT dos flows e teste ponta a ponta. Dizer qual informação adicional seria necessária.

## 7. Inventário resumido

Informar contagens, não despejar objetos completos:

- pastas e flows;
- blocos GPT e assistants únicos/compartilhados;
- skills, User fields, Bot fields e tags;
- campanhas, boards, grupos de keywords e sequências;
- fast replies, motivos de encerramento e presets de agendamento.

Quando um domínio for parcial, acrescentar o denominador conhecido ou indicar “mínimo observado”.

## 8. Próximo passo seguro

Encerrar com uma ação pequena e reversível. Se a principal recomendação envolver um agente GPT, propor criar e testar uma versão isolada usando `$botconversa-agent-upgrade`, sem modificar o original nesta skill. Para outros recursos, apresentar a mudança como plano pendente de aprovação explícita.
