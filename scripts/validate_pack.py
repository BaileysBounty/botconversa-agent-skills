#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
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


def main() -> int:
    errors: list[str] = []
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
        }
        for fragment, label in required_guards.items():
            if fragment not in upgrade_text:
                errors.append(f"Guardrail ausente ({label}): {fragment}")

    if errors:
        print("Falha na validação:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Pack válido: {len(skill_dirs)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
