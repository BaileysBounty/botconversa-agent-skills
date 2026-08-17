# Rubrica de revisão do agente

Use esta rubrica para transformar a configuração observada em recomendações verificáveis. Não atribua nota a uma dimensão sem evidência suficiente.

## Modelo de evidência

Classifique cada afirmação:

- **Observado:** aparece diretamente nas respostas das tools, no prompt ou nas skills carregadas.
- **Inferido:** conclusão plausível, mas depende do comportamento em execução ou de contexto não disponível.
- **Não verificável:** exige conversas, métricas, subscriber data, blocos não GPT ou integrações que o MCP atual não expõe.

Nunca converta uma inferência em fato. Use linguagem como “o prompt indica”, “há risco de” e “precisa ser validado no simulador”.

## Escala

Avalie cada dimensão aplicável de 0 a 3:

- **0 — crítico:** ausente, contraditório ou capaz de impedir o funcionamento.
- **1 — frágil:** existe parcialmente, com lacunas relevantes.
- **2 — adequado:** atende ao caso principal, com melhorias localizadas.
- **3 — sólido:** explícito, coerente e coberto por tratamento de exceções.
- **N/A:** não aplicável ou não observável.

Calcule a nota geral apenas sobre dimensões aplicáveis:

```text
nota = pontos obtidos / (3 × dimensões aplicáveis) × 100
```

Informe também a confiança da avaliação:

- **Alta:** configuração completa e skills lidas; poucas dependências externas.
- **Média:** parte relevante depende de teste manual ou stubs não GPT.
- **Baixa:** alvo incompleto, skills inacessíveis ou arquitetura majoritariamente invisível.

A nota serve para priorizar o trabalho dentro do mesmo agente; não promete desempenho comercial nem deve comparar agentes com escopos diferentes.

## Dimensões

### 1. Objetivo, persona e limites

Verifique se o agent define:

- resultado esperado e público atendido;
- papel que deve assumir e o que não deve fazer;
- critérios claros de sucesso, falha e encaminhamento;
- limites comerciais, jurídicos, financeiros ou de suporte relevantes.

Sinalize objetivo genérico, funções conflitantes ou promessas que excedam as tools disponíveis.

### 2. Instruções e hierarquia de decisão

Verifique:

- ordem operacional inequívoca;
- prioridades em caso de conflito;
- critérios “se/então” em vez de adjetivos vagos;
- ausência de instruções duplicadas ou contraditórias;
- separação entre regras permanentes e dados mutáveis do negócio.

### 3. Conversa e experiência do usuário

Procure:

- abertura compatível com o objetivo;
- uma pergunta por vez quando isso reduzir esforço;
- confirmação de dados sensíveis ou irreversíveis;
- respostas para ambiguidade, recusa, silêncio e mudança de assunto;
- tom, idioma e nível de concisão consistentes.

Não declare que a conversa é boa sem testá-la. A configuração apenas permite estimar o comportamento.

### 4. Conhecimento e políticas do negócio

Confirme se informações necessárias estão presentes no prompt ou em skills e se possuem uma fonte de verdade clara. Detecte:

- placeholders ou informações desatualizadas aparentes;
- regras duplicadas com versões diferentes;
- ausência de política para exceções;
- instrução para inventar quando a informação não existe.

### 5. Coleta e uso de dados

Compare o que o prompt pede com `custom_variable_types`, campos citados e comportamento esperado:

- cada dado tem finalidade clara;
- tipo e descrição são compatíveis;
- dados obrigatórios e opcionais são distinguíveis;
- existe confirmação antes de usar dado crítico;
- não há coleta excessiva ou promessa de persistência sem suporte observável.

### 6. Skills anexadas

Leia o conteúdo completo das skills relevantes. Avalie:

- responsabilidade única e nome compreensível;
- ausência de conflito com o prompt principal;
- regras acionáveis, sem conhecimento redundante;
- anexos realmente necessários;
- impacto do compartilhamento antes de recomendar edição.

### 7. Apps, calendário e capacidades prometidas

Compare `mcp_app_ids`, `google_calendar_ids` e as opções atualmente conectadas com o que o prompt afirma fazer. Trate como crítico quando o agent promete consultar, agendar ou executar algo sem a integração necessária. Não anexe um app apenas para satisfazer o texto; confirme intenção, permissão e conexão.

### 8. Saídas e roteamento

Avalie `custom_outputs` e conexões observáveis:

- nomes representam decisões distintas;
- instruções de saída são testáveis e mutuamente claras;
- sucesso, falha e inatividade têm destino coerente;
- não há saída criada sem tratamento ou referência a saída inexistente.

Quando o destino for um stub não GPT, registre apenas o ID, tipo e nome expostos; não presuma o conteúdo do bloco.

### 9. Recuperação, erro e encaminhamento humano

Verifique `error_message`, tempo de inatividade, instruções de falha e limites de repetição. Busque:

- saída segura quando faltar informação;
- prevenção de loops;
- mensagem útil em erro técnico;
- critério objetivo para encaminhar a humano;
- preservação do contexto necessário ao atendimento.

### 10. Integridade técnica

Inspecione:

- `is_synced` e campos obrigatórios ausentes;
- modo de prompt ativo e uso apenas de seus campos compatíveis;
- modelo, idioma, versão, temperatura e temporizações;
- `shared_with_block_ids`;
- referências a skills, apps, calendários e variáveis válidas;
- conexão inicial e conexões GPT→GPT expostas.

Um assistant não sincronizado, um recurso ausente obrigatório ou uma integração prometida mas desconectada deve preceder melhorias de estilo.

## Priorização dos achados

Classifique cada achado:

- **P0 — bloqueio:** agent não sincroniza, configuração inválida ou comportamento central impossível.
- **P1 — risco alto:** compartilhamento não controlado, contradição central, roteamento quebrado ou ação sem proteção.
- **P2 — oportunidade:** ganho relevante de clareza, cobertura, conversão ou manutenção.
- **P3 — higiene:** nome, organização, redundância pequena ou refinamento editorial.

Para cada achado, registrar: dimensão, classificação de evidência, severidade, evidência concreta, impacto provável, mudança sugerida e forma de testar.

## Regra para recomendações

Recomendar somente mudanças ligadas a um achado. Separar:

1. correção necessária;
2. melhoria recomendada;
3. experimento opcional.

Evitar reescrever todo o prompt por preferência estilística. Preservar regras de negócio, informações e comportamentos que não estejam no escopo aprovado.
