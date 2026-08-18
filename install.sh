#!/usr/bin/env bash

set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
codex_root="${CODEX_HOME:-${HOME:?HOME is required}/.codex}"
destination_root="${BOTCONVERSA_SKILLS_DEST:-$codex_root/skills}"
plugin_root="$repo_root/plugins/botconversa-agent-skills"
version_file="$repo_root/VERSION"
skills=(
  "botconversa-company-checkup"
  "botconversa-agent-upgrade"
  "botconversa-runtime-pack"
)

if [[ $# -gt 0 ]]; then
  echo "Uso: $0" >&2
  exit 1
fi

if [[ ! -f "$version_file" ]]; then
  echo "Pack inválido: VERSION ausente." >&2
  exit 1
fi

pack_version="$(tr -d '[:space:]' < "$version_file")"
if [[ -z "$pack_version" ]]; then
  echo "Pack inválido: VERSION vazio." >&2
  exit 1
fi

if [[ "${BOTCONVERSA_ALLOW_UNRELEASED:-0}" != "1" ]]; then
  expected_tag="v$pack_version"
  current_tag="$(git -C "$repo_root" describe --tags --exact-match HEAD 2>/dev/null || true)"
  if [[ "$current_tag" != "$expected_tag" ]]; then
    echo "Release inválida: o checkout deve estar exatamente na tag $expected_tag." >&2
    exit 1
  fi
  if [[ -n "$(git -C "$repo_root" status --porcelain --untracked-files=all)" ]]; then
    echo "Release inválida: o checkout possui alterações locais." >&2
    exit 1
  fi
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 é necessário para validar o pack antes da instalação." >&2
  exit 1
fi

python3 "$repo_root/scripts/validate_pack.py"

mkdir -p "$destination_root"

for skill in "${skills[@]}"; do
  source_dir="$plugin_root/skills/$skill"
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
  source_dir="$plugin_root/skills/$skill"
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
