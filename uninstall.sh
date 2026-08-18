#!/usr/bin/env bash

set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
codex_root="${CODEX_HOME:-${HOME:?HOME is required}/.codex}"
destination_root="${BOTCONVERSA_SKILLS_DEST:-$codex_root/skills}"
plugin_root="$repo_root/plugins/botconversa-agent-skills"
skills=(
  "botconversa-company-checkup"
  "botconversa-agent-upgrade"
  "botconversa-runtime-pack"
)

if [[ $# -gt 0 ]]; then
  echo "Uso: $0" >&2
  exit 1
fi

for skill in "${skills[@]}"; do
  source_dir="$plugin_root/skills/$skill"
  target="$destination_root/$skill"

  if [[ -L "$target" ]]; then
    current_target="$(readlink "$target")"
    if [[ "$current_target" != "$source_dir" ]]; then
      echo "Conflito: $target pertence a outra instalação. Nada foi removido." >&2
      exit 1
    fi
  elif [[ -e "$target" ]]; then
    echo "Conflito: $target não é um link deste pack. Nada foi removido." >&2
    exit 1
  fi
done

for skill in "${skills[@]}"; do
  source_dir="$plugin_root/skills/$skill"
  target="$destination_root/$skill"
  if [[ -L "$target" && "$(readlink "$target")" == "$source_dir" ]]; then
    rm "$target"
    echo "Removida: $skill"
  else
    echo "Já ausente: $skill"
  fi
done

echo
echo "Somente os links desta release foram removidos. O clone foi preservado em $repo_root."
