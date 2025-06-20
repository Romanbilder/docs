#!/usr/bin/env python3
"""
sanitize_docs.py – Strip Mintlify/Mintfly MDX components from documentation
Run from repository root (same level as docs/). It walks through docs/ and rewrites
all .mdx / .md files to clean Markdown that renders in any standard renderer.

Replacements performed:
  • Remove container tags: CardGroup, Card, Tabs, AccordionGroup, Steps …
  • Convert child tags with title attribute (Tab, Accordion, Step) to Markdown
    headings or list items.
  • Replace Tip / Callout with Markdown blockquotes.
  • Remove any import lines referencing '@mintlify' or 'mintfly'.
  • Strip icon / href attributes implicitly by deleting whole tag.

Before overwriting, a backup with suffix .bak is created next to each file.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

# Directory containing documentation
ROOT_DIR = Path(__file__).resolve().parent
DOCS_DIR = ROOT_DIR  # script placed in docs/ root

# Regex patterns and replacement lambdas
PATTERNS: list[tuple[re.Pattern[str], str | callable[[re.Match[str]], str]]] = [
    # Remove imports from mintlify
    (re.compile(r"^import\s+\{[^}]*\}\s+from\s+['\"]@mintlify/[^'\"]+['\"];?\s*$", re.MULTILINE), ""),
    (re.compile(r"^.*mintfly.*$", re.MULTILINE | re.IGNORECASE), ""),

    # Remove CardGroup, Card container tags
    (re.compile(r"<(/)?CardGroup[^>]*>"), ""),
    (re.compile(r"<(/)?Card[^>]*>"), ""),

    # Tabs container
    (re.compile(r"<(/)?Tabs[^>]*>"), ""),
    # Each Tab with title="..."
    (re.compile(r"<Tab[^>]*title=\"([^\"]+)\"[^>]*>"), lambda m: f"#### {m.group(1)}\n\n"),
    (re.compile(r"</Tab>"), ""),

    # AccordionGroup container
    (re.compile(r"<(/)?AccordionGroup[^>]*>"), ""),
    # Accordion item
    (re.compile(r"<Accordion[^>]*title=\"([^\"]+)\"[^>]*>"), lambda m: f"#### {m.group(1)}\n\n"),
    (re.compile(r"</Accordion>"), ""),

    # Steps container
    (re.compile(r"<(/)?Steps[^>]*>"), ""),
    # Step item – create list entry with automatic numbering placeholder
    (re.compile(r"<Step[^>]*title=\"([^\"]+)\"[^>]*>"), lambda m: f"1. {m.group(1)}\n\n"),
    (re.compile(r"</Step>"), ""),

    # Tip / Callout
    (re.compile(r"<Tip[^>]*>"), "> **Tip:** "),
    (re.compile(r"</Tip>"), ""),

    # Generic self-closing components we don't support
    (re.compile(r"<Video[^>]*/>"), ""),
]

def sanitize_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    original = text
    for pattern, repl in PATTERNS:
        text = pattern.sub(repl, text)

    # Collapse multiple consecutive blank lines to max two
    text = re.sub(r"\n{3,}", "\n\n", text)

    if text != original:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
        path.write_text(text, encoding="utf-8")
        print(f"Sanitized {path}")


def main() -> None:
    for root, _, files in os.walk(DOCS_DIR):
        for fname in files:
            if fname.endswith(('.mdx', '.md')):
                sanitize_file(Path(root) / fname)

if __name__ == "__main__":
    main()
