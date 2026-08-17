#!/usr/bin/env bash

set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
codex_root="${CODEX_HOME:-${HOME:?HOME is required}/.codex}"
destination_root="${BOTCONVERSA_SKILLS_DEST:-$codex_root/skills}"
skills=(
  "botconversa-company-checkup"
  "botconversa-agent-upgrade"
)

if [[ $# -gt 0 ]]; then
  echo "Uso: $0" >&2
  exit 1
fi

mkdir -p "$destination_root"

for skill in "${skills[@]}"; do
  source_dir="$repo_root/skills/$skill"
  target="$destination_root/$skill"

  if [[ ! -f "$source_dir/SKILL.md" ]]; then
    echo "Skill inválida: não encontrei $source_dir/SKILL.md" >&2
    exit 1
  fi

  if [[ -L "$target" ]]; then
    current_target="$(readlink "$target")"
    if [[ "$current_target" != "$source_dir" ]]; then
      echo "Conflito: $target aponta para $current_target. Nada foi substituído." >&2
      exit 1
    fi
  elif [[ -e "$target" ]]; then
    echo "Conflito: $target já existe e não é o link deste pack. Nada foi substituído." >&2
    exit 1
  fi
done

for skill in "${skills[@]}"; do
  source_dir="$repo_root/skills/$skill"
  target="$destination_root/$skill"
  if [[ ! -L "$target" ]]; then
    ln -s "$source_dir" "$target"
    echo "Instalada: $skill"
  else
    echo "Já instalada: $skill"
  fi
done

echo
echo "Pack BotConversa disponível em $destination_root."
echo "Abra uma nova task; se as skills não aparecerem, reinicie o Codex."
