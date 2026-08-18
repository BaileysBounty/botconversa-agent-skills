#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules"}
MAX_FILE_SIZE = 2_000_000
TEXT_SUFFIXES = {
    "",
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}
CONTENT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json"}
APPROVED_REPOSITORY_URLS = {
    "https://github.com/BaileysBounty/botconversa-agent-skills",
}
APPROVED_CODE_FILES = {
    Path("install.sh"),
    Path("scripts/scan_public_content.py"),
    Path("scripts/validate_pack.py"),
    Path("uninstall.sh"),
}
CODE_SUFFIXES = {".go", ".java", ".js", ".php", ".py", ".rb", ".sh", ".ts"}
SOURCE_TREE_NAMES = {"backend", "controllers", "main_app", "migrations", "server", "services", "src"}
FORBIDDEN_NAMES = {
    ".env",
    "credentials.json",
    "service-account.json",
}
FORBIDDEN_SUFFIXES = {
    ".backup",
    ".db",
    ".dump",
    ".key",
    ".log",
    ".p12",
    ".pem",
    ".pfx",
    ".sqlite",
    ".tfstate",
}


@dataclass(frozen=True)
class Rule:
    label: str
    pattern: re.Pattern[str]
    content_only: bool = False


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    label: str


RULES = (
    Rule(
        "texto com codificacao corrompida",
        re.compile(r"\ufffd|\u00c3[\u0080-\u00bf]|\u00c2[\u0080-\u00bf]|\u00e2\u0080[\u0090-\u00bf]"),
    ),
    Rule("caminho local absoluto", re.compile(r"(?<![\w.])/(?:Users|home)/[^/\s]+/")),
    Rule("caminho local do Windows", re.compile(r"\b[A-Za-z]:\\(?:Users|Documents and Settings)\\", re.IGNORECASE)),
    Rule(
        "URL de repositorio nao aprovada",
        re.compile(r"https?://(?:[^\s/@]+@)?(?:www\.)?(?:bitbucket\.org|github\.com|gitlab\.com)/", re.IGNORECASE),
    ),
    Rule(
        "URL de API ou conteudo bruto de repositorio",
        re.compile(
            r"https?://(?:api\.github\.com|raw\.githubusercontent\.com|gist\.githubusercontent\.com|codeload\.github\.com)/",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "URL SSH de repositorio nao aprovada",
        re.compile(r"(?:git@|ssh://git@)(?:bitbucket\.org|github\.com|gitlab\.com)[:/]", re.IGNORECASE),
    ),
    Rule("credencial embutida em URL", re.compile(r"[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s/@]+@", re.IGNORECASE)),
    Rule(
        "credencial em query string",
        re.compile(r"https?://[^\s]+[?&](?:api[_-]?key|access[_-]?token|token|signature|sig|key)=[^\s&#]{12,}", re.IGNORECASE),
    ),
    Rule(
        "cabecalho de autorizacao",
        re.compile(r"(?i)\bauthorization\s*:\s*(?:bearer|basic)\s+[^\s]{12,}"),
    ),
    Rule(
        "cookie de sessao",
        re.compile(
            r"(?i)\b(?:cookie|set-cookie)\s*:\s*[^\n]*(?:session(?:id)?|auth|token|jwt|sid)=[A-Za-z0-9%._~+/=-]{12,}"
        ),
    ),
    Rule(
        "host privado ou de desenvolvimento",
        re.compile(
            r"https?://(?:localhost|127(?:\.\d{1,3}){3}|[^/\s]+\.(?:internal|corp|lan|local)|(?:dev|stage|staging)\.[^/\s]+)",
            re.IGNORECASE,
        ),
    ),
    Rule("endpoint interno", re.compile(r"/(?:api/)?internal(?:_api)?/", re.IGNORECASE)),
    Rule("chave privada", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    Rule("token GitHub", re.compile(r"\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    Rule("chave AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    Rule("chave Google", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    Rule("token Slack", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{20,}\b")),
    Rule("chave OpenAI", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b")),
    Rule("chave Stripe live", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    Rule("JWT completo", re.compile(r"\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\b")),
    Rule(
        "segredo atribuido",
        re.compile(
            r"(?im)^\s*(?:export\s+)?[\"']?(?:[a-z0-9]+[_-])*(?:api[_-]?key|access[_-]?token|token|secret|client[_-]?secret|password|private[_-]?key|cookie|session(?:id)?)[\"']?\s*[:=]\s*(?![\"']?(?:\$\{|\{\{|<|your_|example|dummy|changeme|false\b|true\b|null\b))(?:[\"'][^\"'\n]{12,}[\"']|[A-Za-z0-9_./+=:@!#$%^&*()-]{16,})"
        ),
    ),
    Rule("hash de commit", re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", re.IGNORECASE)),
    Rule(
        "referencia a arquivo de implementacao",
        re.compile(
            r"(?<![\w.-])(?:src|backend|server|services|controllers|migrations|main_app)/[^\s`]+\.(?:py|js|ts|go|rb|java|php)(?::\d+)?",
            re.IGNORECASE,
        ),
        content_only=True,
    ),
    Rule(
        "trecho de implementacao em conteudo publico",
        re.compile(r"(?m)^\s*(?:class\s+[A-Za-z_]\w*|def\s+[A-Za-z_]\w*\s*\(|from\s+[A-Za-z_.]+\s+import\s+|import\s+[A-Za-z_.]+\s*$)"),
        content_only=True,
    ),
)


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file() or path.is_symlink():
            files.append(path)
    return sorted(files)


def scan_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    scannable = text
    for approved_url in APPROVED_REPOSITORY_URLS:
        approved_pattern = re.compile(
            re.escape(approved_url) + r"(?:\.git)?(?=$|[\s)>\]`'\",])"
        )
        scannable = approved_pattern.sub(lambda match: " " * len(match.group(0)), scannable)
    for rule in RULES:
        if rule.content_only and path.suffix.lower() not in CONTENT_SUFFIXES:
            continue
        for match in rule.pattern.finditer(scannable):
            line = scannable.count("\n", 0, match.start()) + 1
            findings.append(Finding(path, line, rule.label))
    return findings


def scan_repository(root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    resolved_root = root.resolve()

    for path in iter_files(root):
        relative = path.relative_to(root)

        if path.is_symlink():
            try:
                path.resolve(strict=True).relative_to(resolved_root)
            except (FileNotFoundError, ValueError):
                findings.append(Finding(relative, 0, "symlink fora do repositorio ou quebrado"))
            continue
        if any(part.lower() in SOURCE_TREE_NAMES for part in relative.parts[:-1]):
            findings.append(Finding(relative, 0, "arvore de codigo-fonte nao aprovada"))
            continue
        if path.suffix.lower() in CODE_SUFFIXES and relative not in APPROVED_CODE_FILES:
            findings.append(Finding(relative, 0, "arquivo de codigo nao aprovado"))
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(Finding(relative, 0, "tipo de arquivo proibido"))
            continue
        if path.stat().st_size > MAX_FILE_SIZE:
            findings.append(Finding(relative, 0, "arquivo grande nao inspecionado"))
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            findings.append(Finding(relative, 0, "formato nao inspecionado"))
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(Finding(relative, 0, "conteudo nao textual"))
            continue

        findings.extend(scan_text(relative, text))

    return findings


def run_self_test() -> int:
    private_key = "-----BEGIN " + "PRIVATE KEY-----"
    cases = (
        ("mojibake", "vers" + chr(0x00C3) + chr(0x00A3) + "o", True),
        ("local path", "/" + "Users/example/private/file.py", True),
        ("private repo", "https://" + "bitbucket.org/example/private", True),
        ("github private repo", "https://" + "github.com/example/private", True),
        ("gitlab private repo", "git@" + "gitlab.com:example/private.git", True),
        ("approved repo", next(iter(APPROVED_REPOSITORY_URLS)), False),
        ("approved repo git", next(iter(APPROVED_REPOSITORY_URLS)) + ".git", False),
        ("approved prefix abuse", next(iter(APPROVED_REPOSITORY_URLS)) + "/private", True),
        ("bearer", "Authorization: " + "Bearer " + "x" * 32, True),
        ("basic auth", "Authorization: " + "Basic " + "e" * 24, True),
        ("session cookie", "Cookie: sessionid=" + "x" * 32, True),
        ("yaml token", "botconversa_token: " + "x" * 32, True),
        ("symbolic password", 'password: "' + "P@ss!word#2026$xy" + '"', True),
        ("json password", '"password": "' + "P@ssw0rd!SuperSecret123" + '"', True),
        ("export api key", "export API_KEY=" + "x" * 32, True),
        ("safe quoted env", '"password": "${PASSWORD}"', False),
        ("signed url", "https://example.com/hook?token=" + "x" * 24, True),
        ("github api", "https://" + "api.github.com/repos/example/private", True),
        ("github raw", "https://" + "raw.githubusercontent.com/example/private/main/file", True),
        ("private key", private_key, True),
        ("source ref", "backend/services/private.py:42", True),
        ("safe env", "${CODEX_HOME:-$HOME/.codex}/skills", False),
        ("safe prose", "Nunca exponha tokens, chaves ou segredos.", False),
        ("safe tool", "Use `get_connection_info` antes de continuar.", False),
    )
    failures: list[str] = []
    for label, sample, should_match in cases:
        matched = bool(scan_text(Path("sample.md"), sample))
        if matched != should_match:
            failures.append(f"{label}: esperado={should_match}, recebido={matched}")

    with tempfile.TemporaryDirectory(prefix="botconversa-public-scan-") as temp_dir:
        fixture_root = Path(temp_dir)
        safe_file = fixture_root / "safe.md"
        safe_file.write_text("Use ${HOME} e dados sinteticos.\n", encoding="utf-8")
        if scan_repository(fixture_root):
            failures.append("repositorio seguro gerou falso positivo")

        forbidden_file = fixture_root / ".env"
        forbidden_file.write_text("PLACEHOLDER=true\n", encoding="utf-8")
        labels = {finding.label for finding in scan_repository(fixture_root)}
        if "tipo de arquivo proibido" not in labels:
            failures.append("arquivo proibido nao foi detectado")
        forbidden_file.unlink()

        external_link = fixture_root / "external-link"
        external_link.symlink_to(fixture_root.parent, target_is_directory=True)
        labels = {finding.label for finding in scan_repository(fixture_root)}
        if "symlink fora do repositorio ou quebrado" not in labels:
            failures.append("symlink externo nao foi detectado")
        external_link.unlink()

        unapproved_code = fixture_root / "private.py"
        unapproved_code.write_text("value = 1\n", encoding="utf-8")
        labels = {finding.label for finding in scan_repository(fixture_root)}
        if "arquivo de codigo nao aprovado" not in labels:
            failures.append("arquivo de codigo nao aprovado nao foi detectado")
        unapproved_code.unlink()

        source_tree = fixture_root / "backend"
        source_tree.mkdir()
        (source_tree / "notes.md").write_text("internal notes\n", encoding="utf-8")
        labels = {finding.label for finding in scan_repository(fixture_root)}
        if "arvore de codigo-fonte nao aprovada" not in labels:
            failures.append("arvore de codigo-fonte nao aprovada nao foi detectada")

    if failures:
        print("Falha no self-test do scanner:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Self-test do scanner: {len(cases) + 5} casos aprovados")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Detecta conteudo que nao deve ser publicado no pack.")
    parser.add_argument("--self-test", action="store_true", help="executa casos sinteticos do scanner")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    findings = scan_repository()
    if findings:
        print("Conteudo bloqueado pela fronteira de publicacao:", file=sys.stderr)
        for finding in findings:
            location = f":{finding.line}" if finding.line else ""
            print(f"- {finding.path}{location}: {finding.label}", file=sys.stderr)
        return 1

    print("Fronteira de publicacao valida: nenhum padrao bloqueado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
