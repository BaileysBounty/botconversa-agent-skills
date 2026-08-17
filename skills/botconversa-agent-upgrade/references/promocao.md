# Promoção segura ao agente original

Promoção é uma operação de produção separada da criação e do teste da v2. Uma aprovação anterior não se estende a esta etapa.

## Pré-condições

Exigir:

- v2 relida e identificada por IDs;
- bateria com evidência suficiente;
- baseline A preservado;
- diff exato entre A e a configuração a promover;
- plano de rollback;
- acesso `write` confirmado;
- limitações e itens manuais declarados.

Se o usuário preferir substituir entradas apontando para a v2 em vez de atualizar o original, tratar isso como outro plano de mudança e não executar com esta autorização.

## Pacote de aprovação

Mostrar imediatamente antes do pedido de consentimento:

1. companhia, flow, GPT block e assistant alvo;
2. campos exatos a alterar e valores antes/depois;
3. skills novas que serão anexadas;
4. campos explicitamente preservados;
5. blocos/flows afetados por compartilhamento;
6. resultado dos testes e riscos restantes;
7. rollback previsto.

Pedir confirmação inequívoca, por exemplo:

> “Autoriza atualizar o GPT block 123 do flow 45 somente nos campos `advanced_assistant_instructions` e `skill_ids`, anexando as skills 901 e 902?”

Consentimento genérico como “pode melhorar” não é suficiente para produção.

## Drift check obrigatório

Depois da aprovação e imediatamente antes da escrita:

1. chamar `get_connection_info` novamente;
2. reler o flow e o GPT block original;
3. reler skills que participam do diff;
4. reler opções de assistant das quais a mudança depende;
5. comparar A' com A conforme [snapshot-e-diff.md](snapshot-e-diff.md).

Se houver drift, não escrever. Mostrar o que mudou, recalcular diff e testes impactados e obter nova aprovação.

## Assistants compartilhados

Sempre inspecionar `shared_with_block_ids` no readback mais recente.

### Regra padrão

Não passar `apply_to_all_blocks=true`. Se a mudança deve afetar apenas o bloco alvo e o assistant é compartilhado:

- tentar uma estratégia de assistant dedicado apenas quando todas as conexões necessárias puderem ser reproduzidas com segurança pelas tools;
- caso contrário, parar e orientar a separação manual no editor.

### Exceção global

Usar `apply_to_all_blocks=true` somente quando:

- todos os block IDs compartilhados forem enumerados;
- cada block estiver associado ao flow correspondente por uma varredura completa de `list_flows` e `list_gpt_blocks`;
- o diff e o efeito esperado em cada flow forem mostrados;
- o usuário consentir explicitamente com esse blast radius completo.

Se qualquer block compartilhado não puder ser associado a um flow, a atualização global é proibida. Expor a limitação não substitui o mapeamento completo.

Uma falha da tool pedindo `apply_to_all_blocks=true` é um aviso de segurança, não uma instrução para repetir automaticamente.

## Skills durante a promoção

Preferir anexar ao agent original as skills clonadas e validadas na v2. Isso isola a mudança de outros assistants que usam as skills antigas.

- Não atualizar uma skill antiga compartilhada apenas para “igualar” a v2.
- Se o usuário quiser substituir globalmente uma skill, mapear consumidores conhecidos, apresentar blast radius e solicitar consentimento separado.
- Reler as skills novas antes de anexá-las.
- Tratar `skill_ids` como substituição da lista quando enviado: incluir todos os IDs que devem permanecer e destacar qualquer remoção.

## Escrita mínima

- Usar `update_gpt_block` com somente os campos aprovados.
- Não enviar valores “por garantia”.
- Lembrar que lista vazia limpa relações.
- Não misturar campos do modo avançado com campos do modo legacy.
- Ao migrar legacy para avançado, mostrar a consolidação completa e aprovar explicitamente a troca de modo.
- Não alterar posição, nome, modelo, temperatura, versão, integrações, outputs ou tempos se não estiverem no diff aprovado.
- Não executar exclusões como parte da promoção.

## Read-after-write

Imediatamente após a operação:

1. chamar `get_gpt_block`;
2. conferir cada campo aprovado e cada campo crítico preservado;
3. verificar `is_synced` e campos obrigatórios ausentes;
4. confirmar `shared_with_block_ids` e relações anexadas;
5. chamar `list_gpt_blocks` para conferir conexões observáveis;
6. reler skills anexadas quando pertinente.

Se o readback divergir:

- não continuar com outras mutações;
- registrar o estado real;
- avaliar se o rollback exato é seguro;
- obter autorização antes de qualquer correção adicional, exceto quando a mesma autorização já tiver definido expressamente um rollback automático para esse caso.

## Rollback

Preparar o payload inverso a partir de A, sem executá-lo antecipadamente. O rollback deve restaurar apenas os campos alterados e os IDs originais de skills/relações.

Oferecer rollback quando:

- o assistant ficar dessincronizado;
- o readback não corresponder ao aprovado;
- um teste de fumaça pós-promoção falhar;
- o usuário solicitar restauração.

Mesmo em incidente, inspecionar compartilhamento antes de restaurar. Um rollback com `apply_to_all_blocks` possui o mesmo blast radius de qualquer outra atualização global.

## Encerramento

Relatar:

- estado final relido;
- campos efetivamente alterados;
- sincronização e compartilhamento;
- evidência disponível e teste de fumaça pendente;
- snapshot usado para rollback;
- flow de teste mantido;
- qualquer limpeza futura, sempre como decisão separada.
