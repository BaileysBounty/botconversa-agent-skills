# Fronteira de publicação e segurança

Este repositório deve conter somente conhecimento operacional necessário para usar o produto com segurança.

## Conteúdo permitido

- workflows, prompts, rubricas e testes sintéticos;
- nomes e contratos de tools aprovados como superfície pública;
- templates de skills sem dados reais de companhias ou contatos;
- scripts locais de instalação e validação deste pack.

## Conteúdo proibido

- código-fonte proprietário, trechos copiados, stack traces ou referências a arquivos da implementação;
- URLs, caminhos, hosts, endpoints ou nomes de repositórios privados;
- credenciais, tokens, chaves, cookies, payloads de autenticação ou exemplos que se pareçam com segredos reais;
- dados pessoais, prompts reais, logs, dumps, screenshots, IDs ou exports de clientes;
- detalhes de vulnerabilidades não publicados e procedimentos que dependam de comportamento interno não documentado;
- hashes de commits, tags de serviços internos ou nomes de classes, funções e migrações proprietárias.

## Regras de contribuição

1. Escrever em termos de comportamento e contrato público, nunca explicar a implementação interna.
2. Usar somente IDs e dados claramente sintéticos em exemplos.
3. Executar `python3 scripts/scan_public_content.py` e `python3 scripts/validate_pack.py` antes de commit, release ou compartilhamento.
4. Submeter qualquer nova tool, campo ou comportamento do MCP a revisão de produto e segurança antes de tratá-lo como contrato público.
5. Não alterar a visibilidade do repositório nem publicar um artefato sem revisar também o histórico Git e os metadados de autoria.

O scanner é um gate adicional, não uma garantia absoluta. A revisão humana desta fronteira continua obrigatória.
