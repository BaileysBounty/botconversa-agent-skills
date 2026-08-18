# BotConversa Agent Skills

Pack de skills para orientar agentes a usar o MCP do BotConversa com contexto de produto, evidências explícitas e mudanças seguras.

O mesmo conteúdo é empacotado para ChatGPT/Codex e Claude. Os manifests de cada plataforma são apenas adaptadores; as skills vivem em uma única árvore e não são duplicadas.

## Skills incluídas

- `botconversa-company-checkup`: inventaria e avalia, somente em leitura, a configuração que o MCP consegue observar. Prioriza até três oportunidades sem confundir ausência com falta de uso.
- `botconversa-agent-upgrade`: revisa um agente GPT, prepara uma versão isolada para teste e promove somente o diff aprovado depois de validação.
- `botconversa-runtime-pack`: cria o pack completo de skills operacionais e o instala em um novo GPT flow de laboratório, com política-base para CRM, handoff, Kanban, agenda, flows, sequências e integrações sem restringir as tools do MCP.

## Pré-requisitos

O connector MCP do BotConversa deve estar conectado e disponível na mesma sessão. As skills não instalam nem autenticam o MCP.

Para usar o agente criado pelo runtime pack, a companhia também precisa ter o app MCP runtime apropriado disponível para o GPT block. A skill verifica apenas o que o connector expõe e deixa o teste comportamental como etapa separada.

## Instalar no ChatGPT e no Codex

Depois da publicação da tag `v0.2.0`, adicione o marketplace privado e instale o plugin:

```bash
codex plugin marketplace add BaileysBounty/botconversa-agent-skills --ref v0.2.0 &&
codex plugin add botconversa-agent-skills@botconversa
```

Reinicie o aplicativo do ChatGPT, abra o diretório de Plugins e confirme que **BotConversa Agent Skills** está instalado. No beta interno, cada pessoa precisa ter acesso ao repositório privado e autenticação Git configurada.

Um administrador do workspace também pode publicar o plugin local para papéis selecionados dentro do próprio workspace. Isso evita que cada membro repita a instalação e não torna o plugin público.

## Instalar no Claude

No Claude ou Claude Desktop, abra **Customize → Plugins → Add marketplace**, informe `BaileysBounty/botconversa-agent-skills` e instale **botconversa-agent-skills**. Essa instalação acompanha a versão atual do marketplace; para fixar exatamente a release `v0.2.0` durante o beta, prefira o comando do Claude Code abaixo.

No Claude Code, o mesmo fluxo pode ser feito por comando:

```bash
claude plugin marketplace add BaileysBounty/botconversa-agent-skills@v0.2.0 &&
claude plugin install botconversa-agent-skills@botconversa --scope user
```

Se a sessão já estiver aberta, execute `/reload-plugins`. Enquanto o repositório for privado, o usuário também precisa ter acesso ao GitHub e credenciais Git válidas.

## Fallback: instalar as skills diretamente no Codex

Cole este comando em uma task do Codex:

```text
$skill-installer instale do repositório BaileysBounty/botconversa-agent-skills,
na ref v0.2.0 e usando o método git, estas skills:

plugins/botconversa-agent-skills/skills/botconversa-company-checkup
plugins/botconversa-agent-skills/skills/botconversa-agent-upgrade
plugins/botconversa-agent-skills/skills/botconversa-runtime-pack
```

O método `git` usa a autenticação já configurada no GitHub. Esse fallback instala somente as skills; o plugin é o caminho recomendado.

## Fallback: instalar por um comando de terminal

Depois da publicação da tag `v0.2.0`:

```bash
gh repo clone BaileysBounty/botconversa-agent-skills "$HOME/.botconversa-agent-skills-v0.2.0" -- --branch v0.2.0 &&
"$HOME/.botconversa-agent-skills-v0.2.0/install.sh"
```

O instalador valida o conteúdo, exige checkout limpo exatamente na tag correspondente a `VERSION`, cria links em `${CODEX_HOME:-$HOME/.codex}/skills` e nunca substitui silenciosamente arquivos existentes. Esse caminho é específico do Codex e existe apenas como compatibilidade.

Para trocar de release, execute `uninstall.sh` no clone atual antes de instalar a próxima. O desinstalador remove apenas links pertencentes àquela instalação e preserva o clone.

## Usar durante o beta

No ChatGPT, selecione **BotConversa Agent Skills** no diretório de Plugins ou mencione o plugin com `@` e escreva o pedido normalmente. Exemplo:

```text
@BotConversa Agent Skills faça um check-up completo da minha companhia e priorize três oportunidades.
```

No Codex, prefira a invocação explícita com `$` para sabermos qual workflow está sendo testado:

```text
$botconversa-company-checkup faça um check-up completo da minha companhia e priorize três oportunidades.
```

```text
$botconversa-agent-upgrade revise meu agente de vendas e prepare uma versão isolada para teste.
```

```text
$botconversa-runtime-pack instale o pack completo em uma nova versão de teste do meu agente de vendas.
```

No Claude, as mesmas skills podem ativar automaticamente pela intenção ou ser chamadas explicitamente, por exemplo:

```text
/botconversa-agent-skills:botconversa-company-checkup faça um check-up completo da minha companhia.
```

O runtime pack sempre apresenta um dry-run antes de escrever. Aprovação para criar o laboratório não autoriza alterar o agente original, conectar entradas de produção ou executar efeitos externos.

## Limites atuais

O pack avalia profundamente agentes GPT e a configuração exposta pelo connector. Ele não deve afirmar que analisou:

- o conteúdo integral de flows não GPT;
- conversas, mensagens ou performance operacional;
- uso real de tags e campos por contatos;
- cards ou movimentações reais do Kanban;
- broadcasts, equipe ou saúde do canal;
- o resultado final de sistemas externos.

O MCP interno determina tecnicamente o subscriber da conversa: operações sobre tags, campos, campanhas, card, flows e sequências afetam somente o contato atual. O agente escolhe o que fazer e qual recurso usar, mas não escolhe outro contato como alvo.

As skills ensinam o agente a descobrir o recurso correto, resolver ambiguidades, evitar duplicidade e loops, confirmar efeitos externos relevantes e verificar resultados. Elas não são allowlists, não removem tools e não exigem permissões técnicas adicionais para o beta ou para a promoção.

Mutações internas podem ser validadas com um contato de teste na companhia. Calendário, convites, webhooks e integrações podem alcançar sistemas externos reais; para esses casos, usar destinos externos de teste. O teste manual continua obrigatório.

## Fronteira de publicação

As skills contêm apenas workflows, prompts, rubricas, manifestos e testes sintéticos. Código-fonte proprietário, endpoints privados, credenciais, dados de clientes, detalhes de implementação e vulnerabilidades não publicadas são proibidos por [SECURITY.md](SECURITY.md).

O scanner bloqueia padrões comuns de vazamento. Antes de tornar o repositório público, também é obrigatório revisar o histórico Git e confirmar com produto e segurança quais contratos de tools podem ser publicados.

## Validar

```bash
python3 scripts/scan_public_content.py --self-test
python3 scripts/scan_public_content.py
python3 scripts/validate_pack.py
claude plugin validate . --strict
claude plugin validate plugins/botconversa-agent-skills --strict
bash -n install.sh uninstall.sh
```

Consulte [tests/acceptance.md](tests/acceptance.md) antes de publicar uma nova versão.
