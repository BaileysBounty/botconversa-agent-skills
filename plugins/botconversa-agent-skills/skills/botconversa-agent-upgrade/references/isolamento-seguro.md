# Isolamento seguro da versão de teste

O objetivo da v2 é permitir experimentação sem mudar comportamento, entradas ou dependências da produção.

## Portão de escrita

Antes de criar qualquer recurso, apresentar:

- flow e GPT block de origem;
- estratégia de isolamento;
- recursos novos previstos;
- limitações conhecidas;
- garantia de que nenhum ponto de entrada de produção será ligado;
- ação exata que será executada.

Prosseguir somente com um pedido explícito e delimitado. Um pedido já explícito como “crie uma v2 separada desse agente” autoriza apenas os recursos descritos para teste. Não autoriza edição, exclusão ou promoção em produção.

## Escolher a estratégia

### Estratégia A — `create_gpt_flow` (preferida)

Usar quando o comportamento relevante couber em um fluxo iniciado diretamente por um GPT, sobretudo `starting step → GPT`.

Vantagens:

- cria flow, starting block e GPT com assistant dedicado;
- evita herdar compartilhamento desconhecido;
- permite construir a configuração aprovada sem tocar o original.

Procedimento:

1. Consultar `list_gpt_assistant_options`.
2. Consolidar prompts legacy em `advanced_assistant_instructions`, pois assistants novos usam modo avançado.
3. Omitir IDs antigos de outputs/variáveis ao criar objetos novos, salvo exigência explícita da tool.
4. Criar com nome `[TESTE] <nome> — v2` e, se possível, em pasta inequivocamente de teste.
5. Reler com `list_gpt_blocks` e `get_gpt_block`.
6. Confirmar assistant dedicado, sincronização e campos obrigatórios.

### Estratégia B — `duplicate_flow` (cópia para inspeção)

Usar somente quando blocos não GPT ou uma estrutura complexa precisarem ser preservados para inspeção. A duplicação copia o conteúdo do flow, mas **não garante isolamento do assistant nem ausência de efeitos externos**. Ações, webhooks, mudanças de campos/tags e outros comportamentos dos blocos não GPT ficam invisíveis ao MCP e podem continuar ativos na cópia.

Imediatamente depois de duplicar:

1. registrar o novo flow ID;
2. listar seus GPT blocks;
3. obter cada GPT block;
4. comparar assistant IDs e `shared_with_block_ids` com o original;
5. não atualizar nenhum assistant compartilhado.

Se houver compartilhamento:

- para arquitetura suportada integralmente pelas tools, usar `add_gpt_block` para criar um assistant dedicado e `connect_gpt_block` para refazer apenas ligações GPT→GPT ou starting step→GPT;
- não sobrescrever conexão ocupada sem mostrar o destino atual e obter consentimento específico;
- se um bloco não GPT alimentar o GPT ou precisar receber sua saída, declarar que o MCP não consegue refazer toda a ligação e solicitar ajuste manual no editor;
- se o isolamento não puder ser provado, manter a duplicata sem mudanças ou abandoná-la como candidata de teste. Nunca “testar” alterando o assistant compartilhado.

Mesmo que o assistant seja separado, a duplicata permanece **bloqueada para execução** até uma pessoa revisar no editor todos os blocos não GPT, suas conexões e efeitos externos e confirmar explicitamente que o ambiente e os dados de teste são seguros. Sem essa confirmação, a duplicata serve apenas para inspeção. Não a chamar de “v2 isolada” nem orientar o usuário a simulá-la.

## Skills do assistant

- Clonar com `create_skill` toda skill cujo prompt será alterado.
- Usar nome inequívoco, como `[TESTE v2] Política comercial`.
- Anexar à v2 o novo ID, não o ID da skill original alterada.
- Reler a skill criada e comparar o prompt.
- Skills sem mudança podem ser reutilizadas, mas registrar que continuam como dependência compartilhada e classificar a v2 como `isolamento parcial`. Para uma v2 realmente isolada e um snapshot congelado, cloná-las também.
- Não usar `update_skill` na construção da v2.

## Configuração e capacidades

- Preservar campos fora do escopo deliberadamente.
- Anexar somente modelo, idioma, versão, MCP apps e calendários atualmente disponíveis e conectados.
- Se o prompt promete uma capacidade indisponível, corrigir a promessa ou pedir que a conexão seja configurada; não fingir que a integração funciona.
- Não tratar seleção de skills como restrição das tools expostas pelo app MCP. Manter no prompt principal as proteções que precisam valer em toda conversa e usar as skills como playbooks para escolher e operar recursos corretamente.
- Respeitar o modo do prompt. Em assistant novo, usar modo avançado; em leitura de legacy, tratar os campos split como fonte para a consolidação proposta.
- Configurar `starter_message` de acordo com `is_starter_for_gpt`: orientação interna e acionável quando `true`; mensagem estática ao contato quando `false`. Não colocar uma saudação pronta no modo de orientação interna. A primeira mensagem real já acompanha a abertura pela IA; usar `{last_message}` somente quando houver razão explícita para citá-la, sem duplicá-la por padrão. No modo estático, a abertura não chama a IA para responder contextualmente à mensagem que acionou o bloco; mostrar no diff que uma intenção já expressa pode receber apenas a saudação fixa e exigir aprovação dessa consequência.
- Escrever `error_message` como fallback técnico estático direto no WhatsApp: não usar placeholders, não redirecionar para o próprio WhatsApp, não expor a integração e não prometer handoff sem rota confirmada.
- Confirmar `is_synced` e `unfilled_required_fields` no readback.

Anexar o app MCP confirmado para preservar a superfície completa de capacidades. O runtime determina o contato atual como alvo das operações subscriber-scoped; as skills não precisam duplicar essa garantia com allowlists.

## Isolamento dos efeitos externos

Um flow e um assistant separados não tornam automaticamente calendários, integrações, mensagens, flows ou sequências externas em recursos de teste.

Antes de qualquer teste comportamental que possa mutar estado:

1. listar cada app, calendário e destino envolvido;
2. confirmar com evidência ou declaração explícita do usuário que o recurso externo é destinado a teste;
3. usar dados sintéticos e um contato de teste para as operações internas;
4. definir como verificar o efeito e como evitar repetição depois de retorno inconclusivo;
5. omitir ou desabilitar a dependência externa quando não existir destino seguro.

Um contato de teste pode validar as operações internas na companhia atual porque o runtime mantém o subscriber da conversa como alvo. Calendários, convites, webhooks e integrações continuam externos: sem destino de teste, limitar esses casos à decisão, à solicitação de dados, ao pedido de confirmação e ao tratamento de indisponibilidade.

## Não conectar a produção

Durante todo o teste, não:

- criar ou atualizar campanha apontando para a v2;
- criar ou atualizar grupo de palavras-chave apontando para a v2;
- adicionar a v2 a sequência;
- substituir conexão do flow original;
- divulgar link como entrada real;
- excluir ou renomear o flow original;
- aplicar mudanças ao assistant original.

O usuário deve abrir e executar a bateria manual somente em um flow criado por `create_gpt_flow` com isolamento confirmado, ou em uma duplicata que já tenha passado pela revisão manual obrigatória de todos os blocos não GPT e efeitos externos. Uma duplicata ainda classificada como “isolamento pendente” não pode ser executada.

Antes de declarar que não existe entrada de produção, conferir por ID do flow:

1. todas as páginas de `list_campaigns`;
2. todas as páginas relevantes de `list_keyword_groups`;
3. `list_sequences` e, para uma verificação exaustiva, os steps retornados por `get_sequence` de cada sequência.

Se a varredura não for completa, dizer apenas que a skill não criou entradas; não afirmar que nenhuma entrada existe.

## Evidência de isolamento

Antes de declarar a v2 pronta, apresentar:

- IDs do flow, GPT block, assistant e skills novas;
- comparação de assistant ID e `shared_with_block_ids`;
- pontos de entrada encontrados, ou evidência da varredura exaustiva que sustenta “nenhum conectado à produção”;
- conexões que o MCP confirmou;
- conexões não GPT que exigem inspeção manual;
- estado de sincronização e campos ausentes;
- dependências ainda compartilhadas, se houver.

Se qualquer item não puder ser confirmado, classificar a versão como “criada, isolamento pendente”, e não como pronta para teste.

Uma duplicata com blocos não GPT só pode sair de “isolamento pendente” após a revisão manual e a confirmação explícita exigidas acima.
