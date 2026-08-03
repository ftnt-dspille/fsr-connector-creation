#!/usr/bin/env python3
"""Lint the workshop content against the VSCode extension's published contract.

The extension emits ``docs-contract.json`` (``npm run contract`` in the
extension repo) listing every command id, on-screen command label, settings key,
view id, and walkthrough step it actually contributes. A vendored copy lives
next to this script so the workshop repo lints standalone in CI.

Rules
-----
ERROR  unknown-id       a ``fortisoar.<something>`` token that is neither a
                        command id nor a settings key
ERROR  stale-title      a ``FortiSOAR: <Title>`` string that no command uses
ERROR  walkthrough-step a walkthrough step title the extension does not ship
WARN   stale-label      a ``... -> <Label>`` menu instruction whose label looks
                        like a command label but does not match one (allowlist
                        in ``docs-contract-ignore.txt`` for non-extension UI)

Usage
-----
    python3 scripts/lint-docs-contract.py                 # lint content/
    python3 scripts/lint-docs-contract.py --strict        # warnings fail too
    python3 scripts/lint-docs-contract.py --coverage      # also report unused
    python3 scripts/lint-docs-contract.py --refresh PATH  # re-vendor contract
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CONTRACT = SCRIPT_DIR / "docs-contract.json"
IGNORE = SCRIPT_DIR / "docs-contract-ignore.txt"
CONTENT = REPO_ROOT / "content"

# `fortisoar.foo` / `fortisoar.fooBar` inside backticks or prose. The negative
# lookahead drops hostnames like `fortisoar.contenthub.fortinet.com` -- a
# trailing dot means the token is a segment of a longer dotted name, not a leaf
# command id.
ID_RE = re.compile(r"\bfortisoar\.[A-Za-z][A-Za-z0-9]*\b(?!\.)")
# `FortiSOAR: Some Command Title` -- the command-palette form.
TITLE_RE = re.compile(r"FortiSOAR:\s*([A-Z][^`*\n|\]]*?)\s*(?=[`*\n|\]]|$)")
# "right-click an operation → Run Operation" -- the menu form. Unicode arrow or
# `->`; capture the trailing label up to sentence-ending punctuation.
ARROW_RE = re.compile(r"(?:→|->)\s*([A-Z][A-Za-z0-9()/ ]{2,40}?)(?=\s*(?:[.,;:]|$|\n|\*\*|`|\|))")


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


def load_contract() -> dict:
    if not CONTRACT.exists():
        sys.exit(
            f"missing {CONTRACT.relative_to(REPO_ROOT)} -- vendor it with:\n"
            f"  python3 scripts/lint-docs-contract.py --refresh "
            f"/path/to/fortisoar-connector-vscode"
        )
    return json.loads(CONTRACT.read_text())


def load_ignore() -> set[str]:
    if not IGNORE.exists():
        return set()
    out = set()
    for raw in IGNORE.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            out.add(line.lower())
    return out


def is_draft(text: str) -> bool:
    """True if the page's TOML/YAML frontmatter marks it `draft: true`.

    Drafts do not ship to the published site, so they are linted only under
    --include-drafts.
    """
    head = text.split("---", 2)
    if len(head) < 3 or head[0].strip():
        return False
    return re.search(r"^draft:\s*true\s*$", head[1], re.MULTILINE | re.IGNORECASE) is not None


def strip_code_blocks(text: str) -> list[str]:
    """Return lines with fenced code blocks blanked out.

    Code samples legitimately contain identifiers that are not UI strings, and
    blanking (rather than dropping) keeps line numbers accurate.
    """
    lines = text.splitlines()
    out, in_fence = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return out


def lint_file(path: Path, contract: dict, ignore: set[str], seen: set[str]) -> list[Finding]:
    commands: dict = contract["commands"]
    settings = set(contract["settings"])
    view_ids = {v["id"] for v in contract["views"]}
    known_ids = set(commands) | settings
    titles = {c["title"].lower(): cid for cid, c in commands.items()}
    labels = {c["label"].lower(): cid for cid, c in commands.items()}
    step_titles = {
        s["title"].lower() for w in contract["walkthroughs"] for s in w["steps"]
    }

    findings: list[Finding] = []
    for lineno, line in enumerate(strip_code_blocks(path.read_text()), start=1):
        for ident in ID_RE.findall(line):
            if ident in known_ids or ident in view_ids:
                seen.add(ident)
            else:
                findings.append(
                    Finding(
                        "error",
                        "unknown-id",
                        path,
                        lineno,
                        f"`{ident}` is not a command id or settings key in the contract",
                    )
                )

        for raw_title in TITLE_RE.findall(line):
            title = f"FortiSOAR: {raw_title}".strip()
            if title.lower() in titles:
                seen.add(titles[title.lower()])
            else:
                near = _closest(raw_title.lower(), labels)
                hint = f" -- did you mean `FortiSOAR: {commands[near]['label']}`?" if near else ""
                findings.append(
                    Finding("error", "stale-title", path, lineno, f"no command titled `{title}`{hint}")
                )

        for raw_label in ARROW_RE.findall(line):
            label = raw_label.strip().lower()
            if label in labels:
                seen.add(labels[label])
                continue
            if label in ignore:
                continue
            near = _closest(label, labels)
            if near:
                findings.append(
                    Finding(
                        "warn",
                        "stale-label",
                        path,
                        lineno,
                        f'menu label "{raw_label.strip()}" does not match any command; '
                        f'closest is "{commands[near]["label"]}" ({near}). '
                        f"Add it to docs-contract-ignore.txt if it is not an extension menu item.",
                    )
                )

        # Walkthrough step titles are documented as bolded table cells.
        for cell in re.findall(r"\*\*([^*]+)\*\*", line):
            probe = cell.strip().lower()
            if probe in step_titles:
                seen.add(f"walkthrough:{probe}")

    return findings


def _closest(needle: str, labels: dict[str, str]) -> str | None:
    """Cheap similarity: shared-word overlap, no stdlib difflib tuning needed."""
    words = set(needle.split())
    best, best_score = None, 0.0
    for label, cid in labels.items():
        lw = set(label.split())
        if not lw:
            continue
        score = len(words & lw) / len(words | lw)
        if score > best_score:
            best, best_score = cid, score
    return best if best_score >= 0.4 else None


def check_walkthrough_table(contract: dict) -> list[Finding]:
    """The install page documents the walkthrough as a table of step titles.

    Every bolded first cell in that table must be a real step title, and every
    shipped step must appear. This is the check that catches a renamed or
    dropped walkthrough step.
    """
    page = CONTENT / "02-setup" / "01-install-vscode-extension.md"
    if not page.exists():
        return []
    shipped = {}
    for w in contract["walkthroughs"]:
        for s in w["steps"]:
            shipped[s["title"].lower()] = s["id"]

    findings: list[Finding] = []
    documented: set[str] = set()
    in_table = False
    for lineno, line in enumerate(strip_code_blocks(page.read_text()), start=1):
        if re.match(r"^\|\s*Step\s*\|", line):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                in_table = False
                continue
            cell = line.split("|")[1].strip()
            if not cell or set(cell) <= set("-: "):
                continue
            title = cell.strip("*").strip()
            if title.lower() in shipped:
                documented.add(title.lower())
            else:
                findings.append(
                    Finding(
                        "error",
                        "walkthrough-step",
                        page,
                        lineno,
                        f'"{title}" is not a walkthrough step the extension ships',
                    )
                )

    if documented:
        for title, sid in shipped.items():
            if title not in documented:
                findings.append(
                    Finding(
                        "error",
                        "walkthrough-step",
                        page,
                        1,
                        f'walkthrough step "{title}" ({sid}) is shipped but not documented',
                    )
                )
    return findings


def refresh(src_repo: Path) -> None:
    src = src_repo / "docs-contract.json"
    if not src.exists():
        sys.exit(f"{src} not found -- run `npm run contract` in the extension repo first")
    shutil.copyfile(src, CONTRACT)
    print(f"vendored {src} -> {CONTRACT.relative_to(REPO_ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--coverage", action="store_true", help="report contract entries no page mentions")
    ap.add_argument("--include-drafts", action="store_true", help="also lint pages marked draft: true")
    ap.add_argument("--refresh", metavar="EXT_REPO", help="re-vendor docs-contract.json from the extension repo")
    args = ap.parse_args()

    if args.refresh:
        refresh(Path(args.refresh).expanduser().resolve())
        return 0

    contract = load_contract()
    ignore = load_ignore()
    seen: set[str] = set()

    findings: list[Finding] = []
    pages = sorted(CONTENT.rglob("*.md"))
    if not args.include_drafts:
        pages = [p for p in pages if not is_draft(p.read_text())]
    for page in pages:
        findings.extend(lint_file(page, contract, ignore, seen))
    findings.extend(check_walkthrough_table(contract))

    errors = [f for f in findings if f.level == "error"]
    warns = [f for f in findings if f.level == "warn"]
    for f in sorted(findings, key=lambda f: (f.level != "error", str(f.path), f.line)):
        print(f.format())

    if args.coverage:
        unused = sorted(set(contract["commands"]) - seen)
        if unused:
            print("\nCommands the workshop never mentions:")
            for cid in unused:
                print(f"  {cid:38} {contract['commands'][cid]['title']}")

    print(
        f"\n{len(pages)} pages linted against {contract['extensionId']} -- "
        f"{len(errors)} error(s), {len(warns)} warning(s)"
    )
    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
