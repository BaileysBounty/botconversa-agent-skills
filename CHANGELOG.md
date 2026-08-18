# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

## [0.2.2] - 2026-08-18

### Fixed

- Impede que agentes novos usem uma saudação pronta no modo em que `starter_message` deve orientar internamente a IA a responder à primeira mensagem real do contato.
- Evita mensagens de erro que recomendam o próprio WhatsApp dentro da conversa, usam placeholders não suportados ou prometem encaminhamento humano sem uma rota confirmada.

### Changed

- O check-up, a revisão isolada e a bateria de aceitação agora verificam juntos `is_starter_for_gpt`, `starter_message` e `error_message` antes de qualquer criação ou promoção.

## [0.2.1] - 2026-08-17

### Changed

- Disponibiliza o pack para instalação pública pelo GitHub no Codex CLI, Codex no ChatGPT Desktop, Claude Code e Claude Cowork.
- Remove a exigência de acesso privado ao repositório e fixa os comandos na release `v0.2.1`.

### Added

- Adiciona a licença MIT para uso, modificação e distribuição do pack.
