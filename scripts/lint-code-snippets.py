#!/usr/bin/env python3
"""Lint the fenced code blocks in workshop content.

Attendees copy-paste these snippets. Nothing else checks that they parse, that
the JSON is shaped like a FortiSOAR ``info.json``, or that a page's "complete
operations.py" actually defines the operations its own "complete info.json"
declares. This does.

Checks
------
ERROR  python-syntax     a ```python block that does not compile
ERROR  json-syntax       a ```json block that is not valid JSON
ERROR  schema            a JSON block that violates the extension's
                         ``resources/info.schema.json`` (whole documents, and
                         ``configuration`` / ``operations`` / single-operation
                         fragments, each against the matching subschema)
ERROR  missing-handler   an operation declared in a page's complete info.json
                         with no matching ``def`` in that page's complete
                         operations.py
WARN   unused-handler    the reverse: a handler the page never declares

Skipping
--------
Put ``<!-- snippet-lint: skip -->`` on the line before a fence to exempt it --
for deliberately broken teaching examples. Say why in the comment.

Usage
-----
    python3 scripts/lint-code-snippets.py                 # lint content/
    python3 scripts/lint-code-snippets.py --strict        # warnings fail too
    python3 scripts/lint-code-snippets.py --refresh PATH  # re-vendor the schema
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - environment guard
    sys.exit("this linter needs jsonschema:  pip install jsonschema")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA = SCRIPT_DIR / "info.schema.json"
CONTENT = REPO_ROOT / "content"

SKIP_MARKER = "snippet-lint: skip"


@dataclass
class Finding:
    level: str  # "error" | "warn"
    rule: str
    path: Path
    line: int
    message: str

    def format(self) -> str:
        rel = self.path.relative_to(REPO_ROOT)
        return f"{self.level.upper():5} {self.rule:16} {rel}:{self.line}  {self.message}"


@dataclass
class Block:
    lang: str
    line: int  # 1-based line of the opening fence
    body: str


def load_schema() -> dict:
    if not SCHEMA.exists():
        sys.exit(
            f"missing {SCHEMA.relative_to(REPO_ROOT)} -- vendor it with:\n"
            f"  python3 scripts/lint-code-snippets.py --refresh "
            f"/path/to/fortisoar-connector-vscode"
        )
    return json.loads(SCHEMA.read_text())


def is_draft(text: str) -> bool:
    head = text.split("---", 2)
    if len(head) < 3 or head[0].strip():
        return False
    return re.search(r"^draft:\s*true\s*$", head[1], re.MULTILINE | re.IGNORECASE) is not None


def extract_blocks(text: str) -> list[Block]:
    """Fenced blocks, with the opening fence's line number and language.

    Indented fences (inside list items or notice shortcodes) count too, so the
    closing fence is matched on its own indentation-insensitive prefix.
    """
    blocks: list[Block] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        if not stripped.startswith("```"):
            i += 1
            continue
        lang = stripped[3:].strip().split()[0] if stripped[3:].strip() else ""
        start = i
        body: list[str] = []
        i += 1
        while i < len(lines) and not lines[i].lstrip().startswith("```"):
            body.append(lines[i])
            i += 1
        i += 1  # step past the closing fence
        skipped = any(SKIP_MARKER in l for l in lines[max(0, start - 2):start])
        if not skipped:
            blocks.append(Block(lang.lower(), start + 1, dedent_fence(body)))
    return blocks


def dedent_fence(body: list[str]) -> str:
    """Strip the common leading indentation an indented fence carries."""
    widths = [len(l) - len(l.lstrip()) for l in body if l.strip()]
    pad = min(widths) if widths else 0
    return "\n".join(l[pad:] if l.strip() else "" for l in body)


# ── individual checks ───────────────────────────────────────────────────────


def check_python(path: Path, block: Block) -> list[Finding]:
    try:
        compile(block.body, str(path), "exec")
    except SyntaxError as e:
        # e.lineno is relative to the block; +block.line lands on the real line.
        line = block.line + (e.lineno or 1)
        return [Finding("error", "python-syntax", path, line, f"{e.msg}")]
    return []


def subschema_for(doc: object, schema: dict) -> tuple[dict, str] | None:
    """Pick the schema slice a JSON block should be validated against.

    Pages show whole info.json documents *and* fragments -- a bare
    ``{"configuration": {...}}``, an ``{"operations": [...]}`` list, or a single
    operation object. Each gets the matching slice; anything else (API response
    samples, curl output) is only checked for being valid JSON.
    """
    if not isinstance(doc, dict):
        return None
    props = schema["properties"]
    if "name" in doc and "version" in doc:
        return schema, "info.json"
    if "configuration" in doc and len(doc) == 1:
        return {"type": "object", "properties": {"configuration": props["configuration"]}}, "configuration"
    if "operations" in doc and len(doc) == 1:
        return {"type": "object", "properties": {"operations": props["operations"]}}, "operations"
    if "operation" in doc:
        return props["operations"]["items"], "operation"
    return None


def check_json(path: Path, block: Block, schema: dict) -> tuple[list[Finding], object | None]:
    try:
        doc = json.loads(block.body)
    except json.JSONDecodeError as e:
        return [Finding("error", "json-syntax", path, block.line + e.lineno, e.msg)], None
    picked = subschema_for(doc, schema)
    if not picked:
        return [], doc
    sub, kind = picked
    findings = []
    validator = jsonschema.Draft7Validator(sub)
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in err.path) or "(root)"
        findings.append(
            Finding("error", "schema", path, block.line, f"{kind} at {where}: {err.message}")
        )
    return findings, doc


# ── page-level cross-check ──────────────────────────────────────────────────

DEF_RE = re.compile(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)


def check_page_consistency(path: Path, blocks: list[Block], docs: list[object]) -> list[Finding]:
    """Cross-check a page's complete operations.py against its complete info.json.

    Only fires when the page shows both in full -- that's the pair a reader
    copies wholesale, and a rename in one without the other is invisible to
    every other check here.
    """
    full_info = next(
        (d for d in docs if isinstance(d, dict) and "name" in d and "operations" in d), None
    )
    # The complete operations.py, not connector.py: handlers are module-level
    # `def check_health(config)`, whereas connector.py's is the method
    # `def check_health(self, config)`.
    full_ops = next(
        (b for b in blocks if b.lang == "python" and "def check_health(config)" in b.body),
        None,
    )
    if not full_info or not full_ops:
        return []

    declared = {
        op["operation"]
        for op in full_info.get("operations", [])
        if isinstance(op, dict) and "operation" in op
    }
    defined = set(DEF_RE.findall(full_ops.body))
    findings = []
    for name in sorted(declared - defined - {"check_health"}):
        findings.append(
            Finding(
                "error",
                "missing-handler",
                path,
                full_ops.line,
                f'info.json declares "{name}" but operations.py defines no def {name}(...)',
            )
        )
    for name in sorted(defined - declared):
        if name.startswith("_") or name == "check_health":
            continue
        findings.append(
            Finding(
                "warn",
                "unused-handler",
                path,
                full_ops.line,
                f'operations.py defines {name}() but info.json declares no such operation',
            )
        )
    return findings


# ── driver ──────────────────────────────────────────────────────────────────


def lint_file(path: Path, schema: dict) -> tuple[list[Finding], int]:
    text = path.read_text()
    if is_draft(text):
        return [], 0
    blocks = extract_blocks(text)
    findings: list[Finding] = []
    docs: list[object] = []
    checked = 0
    for block in blocks:
        if block.lang == "python":
            findings += check_python(path, block)
            checked += 1
        elif block.lang == "json":
            f, doc = check_json(path, block, schema)
            findings += f
            docs.append(doc)
            checked += 1
    findings += check_page_consistency(path, blocks, docs)
    return findings, checked


def refresh(src_repo: Path) -> None:
    src = src_repo / "resources" / "info.schema.json"
    if not src.exists():
        sys.exit(f"no info.schema.json at {src}")
    shutil.copyfile(src, SCHEMA)
    print(f"vendored {src} -> {SCHEMA.relative_to(REPO_ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--refresh", metavar="PATH", help="re-vendor info.schema.json from the extension repo")
    args = ap.parse_args()

    if args.refresh:
        refresh(Path(args.refresh).expanduser().resolve())
        return 0

    schema = load_schema()
    findings: list[Finding] = []
    pages = 0
    snippets = 0
    for path in sorted(CONTENT.rglob("*.md")):
        f, n = lint_file(path, schema)
        if n:
            pages += 1
        snippets += n
        findings += f

    for finding in sorted(findings, key=lambda f: (str(f.path), f.line)):
        print(finding.format())

    errors = sum(1 for f in findings if f.level == "error")
    warns = len(findings) - errors
    print(
        f"\n{snippets} snippet(s) across {pages} page(s) -- {errors} error(s), {warns} warning(s)"
    )
    return 1 if errors or (args.strict and warns) else 0


if __name__ == "__main__":
    raise SystemExit(main())
