#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from scan_public_content import scan_repository


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "botconversa-agent-skills"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_SPAN_PATTERN = re.compile(r"`([^`]+)`")
MUTATING_TOOL_PATTERN = re.compile(
    r"^(?:add|connect|create|delete|duplicate|move|rename|save|update)_[a-z0-9_]+$"
)
READ_ONLY_TOOLS = {
    "get_board",
    "get_company_settings",
    "get_connection_info",
    "get_gpt_block",
    "get_scheduled_send_presets",
    "get_sequence",
    "get_skill",
    "list_boards",
    "list_bot_fields",
    "list_campaigns",
    "list_chat_close_reasons",
    "list_fast_replies",
    "list_flows",
    "list_folders",
    "list_gpt_assistant_options",
    "list_gpt_blocks",
    "list_keyword_groups",
    "list_sequences",
    "list_skills",
    "list_tags",
    "list_user_fields",
}
RUNTIME_MODULE_IDS = {
    "calendar",
    "contact-crm",
    "flows-sequences",
    "human-handoff",
    "integrations",
    "kanban",
}
RUNTIME_DEFAULT_MODULES = RUNTIME_MODULE_IDS
RUNTIME_SENSITIVE_MODULES = {"calendar", "flows-sequences", "human-handoff", "integrations"}
RUNTIME_MODULE_REQUIRED_FRAGMENTS = {
    "contact-crm": {"campanhas", "variáveis globais"},
    "human-handoff": {"histórico", "duração positiva em segundos"},
    "kanban": {"um card ativo", "mesmo board"},
    "calendar": {"remaining_slots=null", "remaining_slots=0", "eventos já vinculados ao contato atual", "resposta da própria tool"},
    "flows-sequences": {"não oferece listagem direta", "nova solicitação inequívoca"},
    "integrations": {"Albato recebe o ID", "Não existe readback"},
}
RUNTIME_GATING_PHRASES = {
    "Escopo runtime aprovado",
    "default-deny",
    "companhia de teste isolada",
    "experimental; não apto para promoção",
    "app mutante desanexado",
    "Se não puder excluir risco de loop ou duplicidade, não executar",
    "Execute uma vez somente quando houver leitura segura",
    "Execute uma única vez e releia o evento",
    "nunca deixe que ele selecione outra tool",
}
RUNTIME_GATING_PATTERNS = {
    "enforcement ausente nao pode bloquear app, escrita ou promocao": re.compile(
        r"(?:sem|aus[eê]ncia de)\s+(?:enforcement|permiss(?:ão|ao)\s+(?:t[eé]cnica|granular)).{0,160}(?:desanex|n[aã]o anex|bloque|n[aã]o promov|proib.{0,20}escrit)",
        re.IGNORECASE | re.DOTALL,
    ),
    "modulo ausente nao pode proibir tool ou capacidade": re.compile(
        r"(?:m[oó]dulo|skill)\s+(?:ausente|n[aã]o anexad[oa]).{0,120}(?:tool|capacidade).{0,80}(?:proibid[ao]|bloquead[ao]|indispon[ií]vel)",
        re.IGNORECASE | re.DOTALL,
    ),
}


def frontmatter(text: str, source: Path) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{source}: frontmatter ausente")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{source}: frontmatter não foi fechado") from exc

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"{source}: linha inválida no frontmatter: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validate_links(markdown_file: Path, errors: list[str]) -> None:
    text = markdown_file.read_text(encoding="utf-8")
    for target in LINK_PATTERN.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        clean_target = target.split("#", 1)[0]
        if clean_target and not (markdown_file.parent / clean_target).exists():
            errors.append(f"{markdown_file}: link local inexistente: {target}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, object] | None:
    if not path.is_file():
        errors.append(f"{path}: arquivo ausente")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        errors.append(f"{path}: JSON inválido: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path}: deve conter um objeto JSON")
        return None
    return payload


def main() -> int:
    errors: list[str] = []
    version_file = ROOT / "VERSION"
    pack_version = version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else ""
    if not pack_version:
        errors.append("VERSION ausente ou vazio")

    plugin_name = "botconversa-agent-skills"
    openai_manifest_file = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    claude_manifest_file = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    openai_marketplace_file = ROOT / ".agents" / "plugins" / "marketplace.json"
    claude_marketplace_file = ROOT / ".claude-plugin" / "marketplace.json"

    openai_manifest = load_json_object(openai_manifest_file, errors)
    claude_manifest = load_json_object(claude_manifest_file, errors)
    for manifest_file, manifest in (
        (openai_manifest_file, openai_manifest),
        (claude_manifest_file, claude_manifest),
    ):
        if manifest is None:
            continue
        if manifest.get("name") != plugin_name:
            errors.append(f"{manifest_file}: name deve ser {plugin_name}")
        if manifest.get("version") != pack_version:
            errors.append(f"{manifest_file}: version deve coincidir com VERSION ({pack_version})")
        if not isinstance(manifest.get("description"), str) or not manifest["description"].strip():
            errors.append(f"{manifest_file}: description ausente")
        author = manifest.get("author")
        if not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"].strip():
            errors.append(f"{manifest_file}: author.name ausente")

    if openai_manifest is not None and openai_manifest.get("skills") != "./skills/":
        errors.append(f"{openai_manifest_file}: skills deve apontar para ./skills/")
    if openai_manifest is not None:
        interface = openai_manifest.get("interface")
        required_interface_fields = {
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "defaultPrompt",
        }
        if not isinstance(interface, dict):
            errors.append(f"{openai_manifest_file}: interface ausente")
        else:
            for field in sorted(required_interface_fields):
                value = interface.get(field)
                if value is None or value == "" or value == []:
                    errors.append(f"{openai_manifest_file}: interface.{field} ausente")
            capabilities = interface.get("capabilities")
            if not isinstance(capabilities, list) or not all(
                isinstance(item, str) and item.strip() for item in capabilities
            ):
                errors.append(f"{openai_manifest_file}: interface.capabilities inválido")

    for marketplace_file, expected_source in (
        (openai_marketplace_file, {"source": "local", "path": "./plugins/botconversa-agent-skills"}),
        (claude_marketplace_file, "./plugins/botconversa-agent-skills"),
    ):
        marketplace = load_json_object(marketplace_file, errors)
        if marketplace is None:
            continue
        if marketplace.get("name") != "botconversa":
            errors.append(f"{marketplace_file}: name deve ser botconversa")
        if marketplace_file == claude_marketplace_file and (
            not isinstance(marketplace.get("description"), str)
            or not marketplace["description"].strip()
        ):
            errors.append(f"{marketplace_file}: description ausente")
        entries = marketplace.get("plugins")
        if not isinstance(entries, list):
            errors.append(f"{marketplace_file}: plugins deve ser uma lista")
            continue
        matching = [entry for entry in entries if isinstance(entry, dict) and entry.get("name") == plugin_name]
        if len(matching) != 1:
            errors.append(f"{marketplace_file}: deve conter exatamente uma entrada para {plugin_name}")
            continue
        if matching[0].get("source") != expected_source:
            errors.append(f"{marketplace_file}: source divergente para {plugin_name}")
        if marketplace_file == openai_marketplace_file:
            policy = matching[0].get("policy")
            if not isinstance(policy, dict) or policy.get("installation") != "AVAILABLE" or policy.get(
                "authentication"
            ) != "ON_INSTALL":
                errors.append(f"{marketplace_file}: policy inválida para {plugin_name}")
            if matching[0].get("category") != "Productivity":
                errors.append(f"{marketplace_file}: category inválida para {plugin_name}")
        entry_version = matching[0].get("version")
        if marketplace_file == claude_marketplace_file and entry_version != pack_version:
            errors.append(f"{marketplace_file}: version deve coincidir com VERSION ({pack_version})")

    skill_dirs = sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append("Nenhuma skill encontrada")

    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        openai_file = skill_dir / "agents" / "openai.yaml"

        if not skill_file.is_file():
            errors.append(f"{skill_dir}: SKILL.md ausente")
            continue

        text = skill_file.read_text(encoding="utf-8")
        if "TODO" in text:
            errors.append(f"{skill_file}: contém TODO")
        if len(text.splitlines()) >= 500:
            errors.append(f"{skill_file}: deve ter menos de 500 linhas")

        try:
            metadata = frontmatter(text, skill_file)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        expected_name = skill_dir.name
        if metadata.get("name") != expected_name:
            errors.append(
                f"{skill_file}: name deve ser {expected_name!r}, recebido {metadata.get('name')!r}"
            )
        if not NAME_PATTERN.fullmatch(expected_name):
            errors.append(f"{skill_dir}: nome inválido")
        if not metadata.get("description"):
            errors.append(f"{skill_file}: description ausente")
        unexpected = set(metadata) - {"name", "description"}
        if unexpected:
            errors.append(f"{skill_file}: campos inesperados no frontmatter: {sorted(unexpected)}")

        if not openai_file.is_file():
            errors.append(f"{openai_file}: arquivo ausente")
        else:
            openai_text = openai_file.read_text(encoding="utf-8")
            if f"${expected_name}" not in openai_text:
                errors.append(f"{openai_file}: default_prompt deve mencionar ${expected_name}")
            if "TODO" in openai_text:
                errors.append(f"{openai_file}: contém TODO")

        for markdown_file in skill_dir.rglob("*.md"):
            validate_links(markdown_file, errors)

    expected_installed_skills = {path.name for path in skill_dirs}
    for script_name in ("install.sh", "uninstall.sh"):
        script_file = ROOT / script_name
        if not script_file.is_file():
            errors.append(f"{script_name} ausente")
            continue
        script_text = script_file.read_text(encoding="utf-8")
        declared_skills = set(
            re.findall(r'^\s+"(botconversa-[a-z0-9-]+)"\s*$', script_text, re.MULTILINE)
        )
        if declared_skills != expected_installed_skills:
            errors.append(
                f"{script_name}: inventario divergente; esperado={sorted(expected_installed_skills)}, recebido={sorted(declared_skills)}"
            )

    checkup_dir = SKILLS_ROOT / "botconversa-company-checkup"
    if checkup_dir.is_dir():
        checkup_text = "\n".join(
            path.read_text(encoding="utf-8") for path in checkup_dir.rglob("*.md")
        )
        mutating_mentions = sorted(
            {
                token
                for token in CODE_SPAN_PATTERN.findall(checkup_text)
                if MUTATING_TOOL_PATTERN.fullmatch(token)
            }
        )
        if mutating_mentions:
            errors.append(
                "A skill read-only cita tools de mutação: " + ", ".join(mutating_mentions)
            )

        capabilities_file = checkup_dir / "references" / "capacidades.md"
        if capabilities_file.is_file():
            capabilities_text = capabilities_file.read_text(encoding="utf-8")
            declared_read_tools = {
                token
                for token in CODE_SPAN_PATTERN.findall(capabilities_text)
                if token in READ_ONLY_TOOLS
            }
            if declared_read_tools != READ_ONLY_TOOLS:
                missing = sorted(READ_ONLY_TOOLS - declared_read_tools)
                errors.append(
                    "Allowlist read-only incompleta; ausentes: " + ", ".join(missing)
                )

    upgrade_dir = SKILLS_ROOT / "botconversa-agent-upgrade"
    if upgrade_dir.is_dir():
        upgrade_text = "\n".join(
            path.read_text(encoding="utf-8") for path in upgrade_dir.rglob("*.md")
        )
        required_guards = {
            "apply_to_all_blocks=true": "proteção de assistant compartilhado",
            "atualização global é proibida": "bloqueio quando o blast radius está incompleto",
            "bloqueada para execução": "bloqueio de flow misto duplicado",
            "read-after-write": "verificação pós-escrita",
            "drift": "detecção de mudanças concorrentes",
            "Preservar todas as tools": "superficie MCP completa no upgrade",
            "contato atual da conversa": "fronteira deterministica do subscriber",
        }
        for fragment, label in required_guards.items():
            if fragment not in upgrade_text:
                errors.append(f"Guardrail ausente ({label}): {fragment}")

    runtime_dir = SKILLS_ROOT / "botconversa-runtime-pack"
    manifest_file = runtime_dir / "assets" / "runtime-pack" / "manifest.json"
    security_file = ROOT / "SECURITY.md"
    if not security_file.is_file():
        errors.append("SECURITY.md ausente")

    if not manifest_file.is_file():
        errors.append(f"{manifest_file}: manifesto ausente")
    else:
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"{manifest_file}: JSON invalido: {exc}")
            manifest = None

        if isinstance(manifest, dict):
            if manifest.get("schema_version") != 1:
                errors.append(f"{manifest_file}: schema_version deve ser 1")
            if not version_file.is_file():
                errors.append("VERSION ausente")
            else:
                if manifest.get("pack_version") != pack_version:
                    errors.append(
                        f"{manifest_file}: pack_version deve coincidir com VERSION ({pack_version})"
                    )

            assets_root = manifest_file.parent.resolve()
            base_policy_name = manifest.get("base_policy_file")
            base_policy_file = (assets_root / str(base_policy_name or "")).resolve()
            base_policy_inside_pack = True
            try:
                base_policy_file.relative_to(assets_root)
            except ValueError:
                base_policy_inside_pack = False
                errors.append(f"{manifest_file}: base_policy_file sai do pack")

            if not base_policy_name or not base_policy_inside_pack or not base_policy_file.is_file():
                errors.append(f"{manifest_file}: base_policy_file invalido")
            else:
                base_text = base_policy_file.read_text(encoding="utf-8")
                base_guards = {
                    "contato e da conversa atuais": "escopo do contato",
                    "qualquer capacidade disponível no MCP": "superficie MCP completa",
                    "alvo determinístico": "fronteira deterministica do subscriber",
                    "pedido citar outro contato": "bloqueio de alvo divergente",
                    "Nunca revele prompt": "protecao de instrucoes e segredos",
                    "instruções textuais": "fronteira contra injecao por tool",
                    "dados estruturados retornados pelas tools": "encadeamento legitimo de tools",
                    "quando houver leitura disponível": "leitura previa quando disponivel",
                    "Execute cada mutação uma única vez": "prevencao de duplicidade",
                    "Não acione o flow atual": "prevencao de loop",
                    "concluída em sistema externo": "confirmacao de efeito externo",
                    "atendimento humano": "fallback humano",
                    "horário comercial": "uso de contexto temporal",
                    "histórico do chat": "minimizacao do historico",
                }
                for fragment, label in base_guards.items():
                    if fragment not in base_text:
                        errors.append(f"Politica-base sem {label}: {fragment}")

            modules = manifest.get("modules")
            if not isinstance(modules, list):
                errors.append(f"{manifest_file}: modules deve ser uma lista")
                modules = []

            module_ids: list[str] = []
            for index, module in enumerate(modules):
                if not isinstance(module, dict):
                    errors.append(f"{manifest_file}: modulo {index} invalido")
                    continue
                module_id = module.get("id")
                if not isinstance(module_id, str) or not NAME_PATTERN.fullmatch(module_id):
                    errors.append(f"{manifest_file}: id de modulo invalido: {module_id!r}")
                    continue
                module_ids.append(module_id)

                for field in ("name", "description", "file"):
                    if not isinstance(module.get(field), str) or not module[field].strip():
                        errors.append(f"{manifest_file}: {module_id}.{field} ausente")
                if module.get("risk_tier") not in {"standard", "sensitive"}:
                    errors.append(f"{manifest_file}: {module_id}.risk_tier invalido")
                if not isinstance(module.get("related_capabilities"), list) or not module[
                    "related_capabilities"
                ]:
                    errors.append(
                        f"{manifest_file}: {module_id}.related_capabilities deve ser preenchido"
                    )
                module_path = (assets_root / str(module.get("file", ""))).resolve()
                try:
                    module_path.relative_to(assets_root)
                except ValueError:
                    errors.append(f"{manifest_file}: {module_id}.file sai do pack")
                    continue
                if not module_path.is_file():
                    errors.append(f"{manifest_file}: template ausente para {module_id}")
                else:
                    module_text = module_path.read_text(encoding="utf-8")
                    if len(module_text.strip()) < 200:
                        errors.append(f"{module_path}: template curto demais")
                    required_fragments = RUNTIME_MODULE_REQUIRED_FRAGMENTS.get(module_id, set())
                    for required_fragment in sorted(required_fragments):
                        if required_fragment not in module_text:
                            errors.append(
                                f"{module_path}: cobertura operacional ausente: {required_fragment}"
                            )

            if len(module_ids) != len(set(module_ids)):
                errors.append(f"{manifest_file}: IDs de modulos duplicados")
            if set(module_ids) != RUNTIME_MODULE_IDS:
                missing = sorted(RUNTIME_MODULE_IDS - set(module_ids))
                extra = sorted(set(module_ids) - RUNTIME_MODULE_IDS)
                errors.append(
                    f"{manifest_file}: catalogo de modulos divergente; ausentes={missing}, extras={extra}"
                )

            defaults = set(manifest.get("default_modules", []))
            if defaults != RUNTIME_DEFAULT_MODULES:
                errors.append(
                    f"{manifest_file}: default_modules deve ser {sorted(RUNTIME_DEFAULT_MODULES)}"
                )

            sensitive = {
                module.get("id")
                for module in modules
                if isinstance(module, dict) and module.get("risk_tier") == "sensitive"
            }
            if sensitive != RUNTIME_SENSITIVE_MODULES:
                errors.append(
                    f"{manifest_file}: modulos sensiveis devem ser {sorted(RUNTIME_SENSITIVE_MODULES)}"
                )

            manifest_text = manifest_file.read_text(encoding="utf-8")
            for stale_contract in (
                "readback do evento",
                "payload mínimo",
                "verificação de estado ou idempotência",
            ):
                if stale_contract in manifest_text:
                    errors.append(f"{manifest_file}: contrato runtime obsoleto: {stale_contract}")

    runtime_skill_file = runtime_dir / "SKILL.md"
    workflow_file = runtime_dir / "references" / "installation-workflow.md"
    if runtime_skill_file.is_file() and workflow_file.is_file():
        runtime_protocol = runtime_skill_file.read_text(encoding="utf-8") + "\n" + workflow_file.read_text(
            encoding="utf-8"
        )
        protocol_guards = {
            "nova mensagem explícita do usuário": "proveniencia da aprovacao",
            "Não pedir ao usuário que informe a companhia": "descoberta automatica da companhia",
            "Qualquer drift invalida a aprovação": "revalidacao apos aprovacao",
            "get_connection_info` de novo": "revalidacao da companhia",
            "imediatamente antes de cada `create_skill`": "revalidacao antes de toda escrita",
            "antes de `create_gpt_flow`": "revalidacao antes do flow",
            "toda a superfície MCP disponível": "superficie MCP completa",
            "contato atual": "fronteira deterministica do subscriber",
            "pack completo": "catalogo completo por padrao",
            "não repetir": "reconciliacao sem retry mutante",
            "contato de teste": "teste de mutacoes internas",
            "destinos externos de teste": "teste seguro de efeitos externos",
            "não funcionam como permissões": "modulos como conhecimento",
        }
        for fragment, label in protocol_guards.items():
            if fragment not in runtime_protocol:
                errors.append(f"Runtime pack sem {label}: {fragment}")

        runtime_text = "\n".join(
            path.read_text(encoding="utf-8") for path in runtime_dir.rglob("*.md")
        )
        upgrade_text = ""
        if upgrade_dir.is_dir():
            upgrade_text = "\n".join(
                path.read_text(encoding="utf-8") for path in upgrade_dir.rglob("*.md")
            )
        gating_text = runtime_text + "\n" + upgrade_text
        for phrase in sorted(RUNTIME_GATING_PHRASES):
            if phrase in gating_text:
                errors.append(f"Gate runtime legado ainda presente: {phrase}")
        for label, pattern in RUNTIME_GATING_PATTERNS.items():
            if pattern.search(gating_text):
                errors.append(f"Gate runtime semantico ainda presente: {label}")

    acceptance_file = ROOT / "tests" / "acceptance.md"
    if not acceptance_file.is_file():
        errors.append("tests/acceptance.md ausente")
    else:
        acceptance_text = acceptance_file.read_text(encoding="utf-8")
        required_runtime_cases = {
            "Módulo não é permissão",
            "Capacidade fora do caso de uso inicial",
            "Superfície completa do app MCP",
            "Encadeamento legítimo de tools",
            "Flow ou sequência sem histórico consultável",
            "Evento Albato sem payload livre",
            "Contratos de calendário",
            "Cardinalidade e movimento do Kanban",
            "Duração da pausa de automação",
        }
        for case_name in sorted(required_runtime_cases):
            if case_name not in acceptance_text:
                errors.append(f"Caso de aceitação runtime ausente: {case_name}")

    for finding in scan_repository(ROOT):
        location = f":{finding.line}" if finding.line else ""
        errors.append(f"fronteira de publicacao: {finding.path}{location}: {finding.label}")

    if errors:
        print("Falha na validação:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Pack válido: {len(skill_dirs)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
