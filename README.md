# BotConversa Agent Skills

Pack interno de skills para orientar agentes a usar o MCP do BotConversa com contexto de produto, evidência explícita e mudanças seguras.

## Skills incluídas

- `botconversa-company-checkup`: inventaria e avalia a configuração que o MCP consegue observar. É somente leitura e prioriza as três melhores oportunidades.
- `botconversa-agent-upgrade`: revisa um agente GPT, prepara uma versão isolada para teste e promove apenas o diff aprovado.

## Pré-requisito

O MCP do BotConversa deve estar conectado e disponível na mesma sessão. As skills não instalam nem autenticam o MCP.

## Instalar pelo Codex

Cole este comando em uma task do Codex:

```text
$skill-installer instale do repositório BaileysBounty/botconversa-agent-skills,
na ref v0.1.1 e usando o método git, estas skills:

skills/botconversa-company-checkup
skills/botconversa-agent-upgrade
```

O repositório é privado. A pessoa precisa ter acesso a ele e estar autenticada no GitHub. As skills ficam disponíveis a partir da próxima interação; se não aparecerem, reinicie o aplicativo e abra uma nova task.

O método `git` é intencional: ele usa a autenticação já configurada no GitHub e evita depender do download direto de um repositório privado.

## Instalar por Git

Quem preferir um comando de terminal pode instalar a release imutável `v0.1.1`:

```bash
gh repo clone BaileysBounty/botconversa-agent-skills "$HOME/.botconversa-agent-skills-v0.1.1" -- --branch v0.1.1 &&
"$HOME/.botconversa-agent-skills-v0.1.1/install.sh"
```

O instalador cria links em `${CODEX_HOME:-$HOME/.codex}/skills` e nunca substitui silenciosamente arquivos ou diretórios existentes.

Uma nova versão deve ser instalada a partir de uma nova tag, depois de revisar as notas da release. A v0.1.1 não faz atualização automática do conteúdo ativo.

Para trocar de release com segurança, remova primeiro apenas os links da versão atual e então instale a nova tag:

```bash
"$HOME/.botconversa-agent-skills-v0.1.1/uninstall.sh"
```

O desinstalador preserva o clone e recusa remover qualquer arquivo ou link que pertença a outra instalação.

## Usar durante o beta

Prefira invocação explícita para sabermos qual workflow está sendo testado:

```text
$botconversa-company-checkup faça um check-up completo da minha companhia e priorize três oportunidades.
```

```text
$botconversa-agent-upgrade revise meu agente de vendas e prepare uma versão isolada para teste.
```

## Limites atuais

O pack avalia profundamente agentes GPT e a configuração exposta pelo MCP. Ele não deve afirmar que analisou:

- o conteúdo integral de flows não GPT;
- conversas, mensagens ou performance operacional;
- uso real de tags e campos por subscribers;
- cards ou movimentações do Kanban;
- broadcasts, equipe ou saúde do canal.

Consulte [`tests/acceptance.md`](tests/acceptance.md) antes de publicar uma nova versão.

## Validar

```bash
python3 scripts/validate_pack.py
```
