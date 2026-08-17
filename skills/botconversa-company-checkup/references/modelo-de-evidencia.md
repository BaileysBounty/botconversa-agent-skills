# Modelo de evidência

Classifique toda conclusão em uma das categorias abaixo. Não misture fato e interpretação na mesma frase.

## 1. Confirmado

Use quando uma tool retornou diretamente o fato ou quando a conclusão é uma comparação determinística entre resultados completos.

Exemplos:

- “O agente do bloco `813` está com `is_synced=false` e lista `starter_message` em `unfilled_required_fields`.”
- “O mesmo `assistant_id` é compartilhado pelos blocos `813` e `992`, conforme `shared_with_block_ids`.”
- “Não há board cadastrado” somente após percorrer todas as páginas de `list_boards`.

Sempre registrar:

- tool de origem;
- ID e nome do recurso, quando existirem;
- campos relevantes, sem expor segredos;
- cobertura usada na comparação.

## 2. Inferido

Use quando houver indícios, mas a conclusão depender de intenção, semântica do prompt, contexto do negócio ou uma área não exposta.

Exemplos:

- “O prompt solicita data de nascimento, mas não encontrei um User field correspondente; confirme onde esse dado deve ser persistido.”
- “A estrutura parece representar um funil comercial e pode se beneficiar de um board.”
- “As instruções do agente e de uma skill parecem se contradizer.”

Apresentar como hipótese verificável. Incluir o motivo da inferência e uma pergunta ou teste de validação. Nunca usar “está errado” quando a intenção não é conhecida.

## 3. Não verificável

Use quando a informação necessária não é exposta pelas tools atuais.

Exemplos:

- taxa de conversão do agente;
- qualidade das conversas;
- uso real de uma tag ou fast reply;
- conteúdo completo e todos os caminhos de um flow misto;
- desempenho individual de operadores.

Não substituir a falta de evidência por uma estimativa. Explicar qual dado ou tool seria necessário para verificar.

## Regras para ausência e uso

- Ausência confirmada: “Nenhum board foi retornado após 1/1 página.”
- Necessidade inferida: “Pelos sinais X e Y, um board pode ajudar.”
- Uso desconhecido: “A tag não aparece nas referências expostas.”
- Formulação proibida: “A tag não é usada.”

Não confundir criação recente, nome genérico, zero em um contador sem período ou falta de descrição com abandono.

## Formato mínimo de cada achado

```text
Prioridade: P0 | P1 | P2 | P3
Classificação: Confirmado | Inferido | Não verificável
Observação: fato ou hipótese em uma frase
Evidência: tool, recurso/ID e campos relevantes
Impacto possível: consequência, sem exagerar certeza
Sugestão: ação concreta e reversível
Validação: como confirmar antes de alterar produção
```

Use confiança `Alta` para fatos diretos e comparações determinísticas completas, `Média` para correlações semânticas fortes e `Baixa` para hipóteses frágeis. Não dê confiança alta a um domínio com cobertura parcial.

## Privacidade e concisão

- Não reproduzir prompts completos, valores sensíveis de Bot fields ou outros dados desnecessários.
- Citar apenas o trecho mínimo para explicar uma inconsistência semântica.
- Não expor tokens, chaves, URLs secretas ou conteúdo não necessário ao diagnóstico.
