# Regras priorizadas de check-up

Aplicar as regras somente após concluir o inventário pertinente. Um mesmo sinal pode gerar prioridade diferente conforme a evidência; explicitar a classificação.

## P0 — quebra confirmada

Reservar P0 para uma configuração explicitamente inválida ou incapaz de executar como configurada.

### GPT-P0-01 — assistant de entrada não sincronizado

- Condição: `is_synced=false` em `get_gpt_block` e o flow é referenciado por uma entrada ativa exposta.
- Evidência: incluir `unfilled_required_fields` e, quando relevante, `openai_api_key_connected`.
- Recomendação: completar apenas os campos reportados e validar em uma versão de teste; não editar nesta skill.
- Cuidado: sem evidência de entrada ativa, o estado não sincronizado continua confirmado, mas deve ser classificado como P1 porque o flow pode ser rascunho ou ser acionado por uma área não exposta.

### GPT-P0-02 — dependência configurada indisponível

- Condição: ID de app MCP ou calendário configurado no assistant de um flow com entrada ativa não consta como conectado/disponível em `list_gpt_assistant_options`.
- Cuidado: se a lista de opções falhou, classificar como não verificável, não como quebra.
- Sem evidência de entrada ativa, rebaixar para P1 e pedir confirmação do status do flow.

### ENTRY-P0-01 — entrada ativa aponta para referência ausente

- Condição: campanha, grupo de keyword ligado ou passo ativo de sequência referencia um flow que não existe no inventário completo.
- Cuidado: uma referência nula opcional em recurso desligado não é P0.

### ENTRY-P0-02 — flow acionado sem próximo passo visível

- Condição: flow referenciado por uma entrada ativa possui starting step explicitamente sem alvo.
- Cuidado: se houver alvo não GPT como stub, não avaliar sua lógica; o flow permanece parcial.

### KEYWORD-P0-01 — grupo ativo inviável

- Condição: grupo ligado sem flow ou sem palavras-chave.
- Evidência: estado, flow e quantidade de keywords retornados pela mesma configuração.

### SEQUENCE-P0-01 — passo ativo inválido

- Condição determinística: passo ativo sem flow; passo não imediato sem atraso válido; janela restrita sem início/fim; dias restritos sem dia configurado.
- Cuidado: passos desligados podem ser rascunhos intencionais.

## P1 — risco operacional confirmado

### GPT-P1-01 — assistant compartilhado

- Condição: `shared_with_block_ids` não vazio.
- Fato: uma atualização no assistant afeta todos os blocos compartilhados.
- Não afirmar que o compartilhamento é incorreto; recomendar mapa de impacto e versão isolada antes de editar.

### GPT-P1-02 — chave OpenAI ausente com agentes GPT

- Condição: existem blocos GPT e `openai_api_key_connected=false`.
- Relacionar com `is_synced`; se todos estiverem sincronizados, apresentar como risco/configuração a confirmar, não quebra.

### SKILL-P1-01 — instruções incompatíveis

- Condição: prompt do assistant e prompts das skills anexadas contêm instruções mutuamente excludentes sobre objetivo, tom, coleta, transferência ou uso de ferramentas.
- Classificação: `Inferido`, pois exige interpretação semântica.
- Citar apenas trechos mínimos e pedir validação da intenção do negócio.

### RUNTIME-P1-01 — ação sensível prometida sem proteção observável

- Sinal: prompt ou skill promete agendamento, integração externa, acionamento de automação ou outra mutação relevante, mas não há regra observável de contato atual, recurso inequívoco, confirmação proporcional, prevenção de duplicidade, tratamento de retorno inconclusivo e handoff.
- Classificação: `Inferido`, porque o connector não executa a conversa nem expõe necessariamente a permissão granular de cada tool runtime.
- Manter P1 somente quando a ação sensível for parte central e explicitamente prometida pelo agente; caso contrário, classificar como P2.
- Recomendação: validar a intenção e preparar política-base mais o pack operacional completo em uma versão de teste com a skill `botconversa-runtime-pack`, destacando os módulos mais relevantes para aquele agente.

### KEYWORD-P1-01 — sobreposição de keywords ativas

- Condição: o mesmo termo normalizado aparece em mais de um grupo ativo e os tipos de correspondência podem competir.
- Comparar termo, tipo, flow e estado; não sinalizar grupos desligados como risco operacional atual.

### SEQUENCE-P1-01 — subscribers sem passo ativo

- Condição: `total_subscribers > 0` e nenhum passo está ligado, ou um passo ativo referencia configuração incompleta sem satisfazer P0 por incerteza do retorno.
- Não deduzir abandono apenas por passos desligados quando o total for zero ou desconhecido.

### BOARD-P1-01 — estrutura terminal inconsistente

- Condição: nenhuma coluna final ou mais de uma coluna final em um board que deveria encerrar cards segundo as próprias regras expostas.
- Se a finalidade do board não for clara, classificar a necessidade de coluna final como inferida.

## P2 — oportunidade contextual

P2 exige indícios positivos do caso de uso. A simples ausência de um recurso não basta.

### DATA-P2-01 — dado solicitado sem campo correspondente visível

- Sinal: agente pede um dado persistente e não há User field semanticamente correspondente.
- Classificação: `Inferido` por causa da cobertura parcial dos flows.
- Pergunta de validação: onde o dado é salvo hoje e qual tipo deveria ter?

### BOARD-P2-01 — processo com etapas sem Kanban correspondente

- Sinais possíveis: prompts, nomes de flows, campos ou tags descrevem qualificação, handoff, venda, agendamento ou status; nenhum board representa esse processo.
- Confirmar apenas que o board não existe; classificar sua necessidade como inferida.

### SERVICE-P2-01 — biblioteca de atendimento não acompanha o processo

- Sinais: existe contexto explícito de atendimento humano e fast replies estão vazias, ou motivos de encerramento estão habilitados e vazios.
- Não afirmar baixa produtividade ou baixa adoção sem chats e dados de operadores.

### GPT-P2-01 — capacidade prometida sem configuração correspondente

- Sinais: prompt promete agenda ou app MCP específico, mas o assistant não possui a integração configurada.
- Se a opção está indisponível, pode subir para P0/P1; se a promessa veio apenas da interpretação textual, manter como `Inferido`.

### RUNTIME-P2-01 — operação repetitiva compatível com módulo runtime

- Sinais: o objetivo e as regras observadas exigem de forma recorrente CRM do contato, handoff, Kanban, agenda, flows, sequências ou integração externa; o agente ainda concentra essas regras no prompt ou não possui instrução operacional específica.
- Confirmar o caso de uso e a opção de app MCP disponível antes de recomendar instalação.
- Recomendar o pack completo para preservar o conhecimento de toda a superfície MCP e destacar os módulos que resolvem o comportamento observado. Não afirmar que um módulo restringe permissões ou tools.
- Próximo passo: dry-run de um novo flow de laboratório com a skill `botconversa-runtime-pack`; nenhuma alteração nesta skill.

### SKILL-P2-01 — conhecimento repetido e pouco modular

- Sinal: instruções extensas e equivalentes repetidas em vários assistants, sem skill reutilizável correspondente.
- Sugerir modularização somente quando a repetição for comprovada; assistants compartilhados podem explicar a igualdade.

### ENTRY-P2-01 — canal de entrada compatível não configurado

- Sinal: o caso de uso explicitamente pede aquisição, reengajamento ou palavra-chave e não existe campanha, keyword ou sequência correspondente.
- Não recomendar todos os canais; escolher apenas o que resolve a intenção observada.

## P3 — higiene e organização

### NAMING-P3-01 — nomes ambíguos ou quase duplicados

- Comparar nomes normalizados de flows, skills, campos, tags, boards e sequências.
- Nomes como “teste” ou “novo” são indícios, não prova de problema. Mostrar exemplos e pedir confirmação antes de renomear.

### FOLDER-P3-01 — navegação difícil

- Sinal: muitos flows fora de pastas ou estrutura profundamente fragmentada.
- Não aplicar limite universal rígido; explicar o padrão observado e propor organização reversível.

### DOC-P3-01 — descrições ausentes em escala

- Sinal: proporção relevante de skills, campos, tags ou boards sem descrição em uma conta complexa.
- Tratar como manutenção, nunca como quebra operacional.

## Seleção das recomendações principais

Ordenar por:

1. P0 antes de P1, P2 e P3;
2. `Confirmado` antes de `Inferido` dentro da mesma prioridade;
3. maior número de entradas ou agentes afetados, quando isso for comprovado;
4. maior risco de mudança em cascata;
5. menor esforço para validar com segurança.

Não preencher artificialmente um “top 3”. Se houver apenas um achado forte, entregar um principal e manter hipóteses na seção de oportunidades.
