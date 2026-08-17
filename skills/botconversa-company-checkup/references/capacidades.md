# Capacidades e limites do MCP

Use somente as 21 operações abaixo durante o check-up. Qualquer tool BotConversa ausente desta lista é proibida nesta skill.

## Allowlist read-only

| Domínio | Tools permitidas | O que comprovam | Limite importante |
|---|---|---|---|
| Conexão | `get_connection_info` | Companhia conectada, proprietário autenticado e acesso `read` ou `write` | Não comprova saúde da operação |
| Configurações | `get_company_settings` | Fuso, idioma, motivos de encerramento habilitados e presença de chave OpenAI | Expõe somente essas configurações |
| Flows e pastas | `list_folders`, `list_flows` | Árvore de pastas; IDs, nomes, criação e pasta dos flows | Não retorna o conteúdo geral do flow |
| Agentes GPT | `list_gpt_blocks`, `get_gpt_block`, `list_gpt_assistant_options` | Starting step, blocos GPT, configuração completa, outputs, compartilhamento do assistant, opções de modelo/idioma/apps/calendários | Blocos não GPT aparecem apenas como `{id, type, name}` quando são alvos visíveis |
| Skills de IA | `list_skills`, `get_skill` | Inventário, descrição e prompt completo de cada skill | Referências fora dos agentes GPT expostos não são observáveis |
| Campos | `list_user_fields`, `list_bot_fields` | Definições, tipos, descrições e valores de Bot fields | Não comprova preenchimento nem uso por subscribers |
| Tags | `list_tags` | Definições, descrições e cores | Não mostra subscribers associados nem uso completo em flows |
| Campanhas | `list_campaigns` | Link, texto, flow de destino e contadores retornados | Não é broadcast; não inventar período para os contadores |
| Kanban | `list_boards`, `get_board` | Boards, colunas, posição, coluna final e regras | Não retorna cards nem movimentações |
| Palavras-chave | `list_keyword_groups` | Grupos, termos, tipo de correspondência, flow e estado | Não comprova volume de acionamentos |
| Sequências | `list_sequences`, `get_sequence` | Nome, total informado de subscribers, passos, flow, atrasos, janelas e estado | Não permite inspecionar subscribers da sequência |
| Atendimento | `list_fast_replies`, `list_chat_close_reasons`, `get_scheduled_send_presets` | Bibliotecas configuradas para operadores | Não retorna chats, mensagens nem adoção pelos operadores |

## Cobertura de flows

Classifique flows como `Parcial` em todos os relatórios, ainda que todas as chamadas tenham sido concluídas. É possível confirmar:

- metadados e pasta do flow;
- starting step e seu alvo visível;
- configuração e conexões dos blocos GPT;
- stubs de blocos não GPT quando aparecem como alvos de uma conexão exposta;
- referências ao flow em campanhas, palavras-chave e sequências.

Não é possível confirmar:

- texto de mensagens e menus;
- lógica interna de condições;
- ações, webhooks e manipulação de campos ou tags em blocos não GPT;
- todos os caminhos e saídas de um flow misto;
- execução ponta a ponta ou resultado de uma conversa.

## Áreas não expostas hoje

Marque como `Indisponível`, sem tentar deduzir por proxies:

- busca, perfil, tags, campos, sequências e ações de subscribers;
- chats, histórico de mensagens, mensagens agendadas e atuação de operadores;
- cards do Kanban e movimentações de pipeline;
- broadcasts e templates de WhatsApp;
- managers, permissões de equipe e produtividade por operador;
- saúde do canal WhatsApp, qualidade do número e limites;
- dashboard geral e métricas completas de automação;
- simulador/teste automatizado de agentes.

## Interpretação segura

- Um recurso existente pode ser legado, teste ou produção; o MCP não informa isso por padrão.
- Um recurso sem referência visível pode ser usado em uma área não exposta.
- Um contador retornado é evidência somente do valor e do contexto explicitamente fornecidos pela tool.
- Um objeto ausente é um fato de configuração; dizer que ele “faz falta” exige evidência contextual e deve ser classificado como inferência.
