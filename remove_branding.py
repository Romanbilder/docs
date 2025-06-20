#!/usr/bin/env python3
"""
remove_branding.py – Delete any line that contains the Mintlify / mintfly branding.

Usage:
  python remove_branding.py

Creates a .bak backup of each modified file (original content) the first time it
changes that file. Only touches .mdx and .md files under the current directory.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
KEYWORDS = re.compile(r"mintlify|mintfly", re.IGNORECASE)

def clean_file(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    cleaned_lines: list[str] = []
    modified = False
    for line in original.splitlines(keepends=True):
        if KEYWORDS.search(line):
            # Skip entire line (remove branding)
            modified = True
            continue
        cleaned_lines.append(line)

    if modified:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
        path.write_text("".join(cleaned_lines), encoding="utf-8")
        print(f"Branding removed from {path.relative_to(DOCS_DIR)}")

def main() -> None:
    for root, _, files in os.walk(DOCS_DIR):
        for fname in files:
            if fname.endswith((".mdx", ".md")):
                clean_file(Path(root) / fname)

if __name__ == "__main__":
    main()
