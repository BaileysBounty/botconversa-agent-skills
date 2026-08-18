# BotConversa Agent Skills

Pack de skills para orientar agentes a usar o MCP do BotConversa com contexto de produto, evidências explícitas e mudanças seguras.

O mesmo conteúdo é empacotado para Codex CLI, Codex no ChatGPT Desktop, Claude Cowork e Claude Code. Os manifests de cada plataforma são apenas adaptadores; as skills vivem em uma única árvore e não são duplicadas.

## Skills incluídas

- `botconversa-company-checkup`: inventaria e avalia, somente em leitura, a configuração que o MCP consegue observar. Prioriza até três oportunidades sem confundir ausência com falta de uso.
- `botconversa-agent-upgrade`: revisa um agente GPT, prepara uma versão isolada para teste e promove somente o diff aprovado depois de validação.
- `botconversa-runtime-pack`: cria o pack completo de skills operacionais e o instala em um novo GPT flow de laboratório, com política-base para CRM, handoff, Kanban, agenda, flows, sequências e integrações sem restringir as tools do MCP.

## Pré-requisitos

O connector MCP do BotConversa deve estar conectado e disponível na mesma sessão. As skills não instalam nem autenticam o MCP.

Para usar o agente criado pelo runtime pack, a companhia também precisa ter o app MCP runtime apropriado disponível para o GPT block. A skill verifica apenas o que o connector expõe e deixa o teste comportamental como etapa separada.

## Instalar no Codex CLI ou no Codex do ChatGPT Desktop

Adicione o marketplace deste repositório público e instale a release `v0.2.2`:

```bash
codex plugin marketplace add BaileysBounty/botconversa-agent-skills --ref v0.2.2 &&
codex plugin add botconversa-agent-skills@botconversa
```

Se usar o Codex no ChatGPT Desktop, reinicie o aplicativo, abra o diretório de Plugins e confirme que **BotConversa Agent Skills** está instalado. Como o repositório é público, não é necessário ter acesso ao BaileysBounty nem autenticar no GitHub.

Esse fluxo instala o marketplace no Codex CLI e no Codex do ChatGPT Desktop. A instalação direta de um marketplace GitHub no ChatGPT web pessoal ainda não é suportada; essa superfície depende da publicação no diretório universal de Plugins da OpenAI. A extensão IDE do Codex também não carrega plugins.

Se o marketplace privado da `v0.2.0` já estiver configurado, remova a instalação antiga antes de adicionar a fonte pública:

```bash
codex plugin remove botconversa-agent-skills@botconversa &&
codex plugin marketplace remove botconversa &&
codex plugin marketplace add BaileysBounty/botconversa-agent-skills --ref v0.2.2 &&
codex plugin add botconversa-agent-skills@botconversa
```

## Instalar no Claude

No Claude Cowork, dentro do aplicativo Desktop, abra **Customize → Plugins → Add marketplace**, informe `BaileysBounty/botconversa-agent-skills` e instale **botconversa-agent-skills**. Também é possível informar a URL completa `https://github.com/BaileysBounty/botconversa-agent-skills`.

No Claude Code, fixe a release por comando:

```bash
claude plugin marketplace add BaileysBounty/botconversa-agent-skills@v0.2.2 &&
claude plugin install botconversa-agent-skills@botconversa --scope user
```

No Claude Code, se a sessão já estiver aberta, execute `/reload-plugins`. Não é necessário autenticar no GitHub para instalar o repositório público. Este guia cobre Claude Cowork e Claude Code; o Claude Chat comum não faz parte da instalação validada nesta release.

Para substituir o marketplace privado da `v0.2.0` no Claude Code:

```bash
claude plugin uninstall botconversa-agent-skills@botconversa &&
claude plugin marketplace remove botconversa &&
claude plugin marketplace add BaileysBounty/botconversa-agent-skills@v0.2.2 &&
claude plugin install botconversa-agent-skills@botconversa --scope user
```

## Fallback: instalar as skills diretamente no Codex

Cole este comando em uma task do Codex CLI ou do Codex no ChatGPT Desktop:

```text
$skill-installer instale do repositório BaileysBounty/botconversa-agent-skills,
na ref v0.2.2 e usando o método git, estas skills:

plugins/botconversa-agent-skills/skills/botconversa-company-checkup
plugins/botconversa-agent-skills/skills/botconversa-agent-upgrade
plugins/botconversa-agent-skills/skills/botconversa-runtime-pack
```

Esse fallback instala somente as skills; o plugin é o caminho recomendado.

## Fallback: instalar por um comando de terminal

```bash
git clone --depth 1 --branch v0.2.2 https://github.com/BaileysBounty/botconversa-agent-skills.git "$HOME/.botconversa-agent-skills-v0.2.2" &&
"$HOME/.botconversa-agent-skills-v0.2.2/install.sh"
```

O instalador valida o conteúdo, exige checkout limpo exatamente na tag correspondente a `VERSION`, cria links em `${CODEX_HOME:-$HOME/.codex}/skills` e nunca substitui silenciosamente arquivos existentes. Esse caminho é específico do Codex e existe apenas como compatibilidade.

Para trocar de release, execute `uninstall.sh` no clone atual antes de instalar a próxima. O desinstalador remove apenas links pertencentes àquela instalação e preserva o clone.

## Usar

No Codex do ChatGPT Desktop, selecione **BotConversa Agent Skills** no diretório de Plugins ou mencione o plugin com `@` e escreva o pedido normalmente. Exemplo:

```text
@BotConversa Agent Skills faça um check-up completo da minha companhia e priorize três oportunidades.
```

No Codex CLI ou no Codex do ChatGPT Desktop, use a invocação explícita com `$` quando quiser selecionar o workflow:

```text
$botconversa-company-checkup faça um check-up completo da minha companhia e priorize três oportunidades.
```

```text
$botconversa-agent-upgrade revise meu agente de vendas e prepare uma versão isolada para teste.
```

```text
$botconversa-runtime-pack instale o pack completo em uma nova versão de teste do meu agente de vendas.
```

No Claude Cowork ou Claude Code, as mesmas skills podem ativar automaticamente pela intenção ou ser chamadas explicitamente, por exemplo:

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

As skills ensinam o agente a descobrir o recurso correto, resolver ambiguidades, evitar duplicidade e loops, confirmar efeitos externos relevantes e verificar resultados. Elas não são allowlists, não removem tools e não exigem permissões técnicas adicionais para a instalação ou para a promoção.

Mutações internas podem ser validadas com um contato de teste na companhia. Calendário, convites, webhooks e integrações podem alcançar sistemas externos reais; para esses casos, usar destinos externos de teste. O teste manual continua obrigatório.

## Fronteira de publicação

As skills contêm apenas workflows, prompts, rubricas, manifestos e testes sintéticos. Código-fonte proprietário, endpoints privados, credenciais, dados de clientes, detalhes de implementação e vulnerabilidades não publicadas são proibidos por [SECURITY.md](SECURITY.md).

O scanner bloqueia padrões comuns de vazamento. Antes de cada release, também é obrigatório revisar o diff, o histórico Git e os metadados públicos.

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

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).
