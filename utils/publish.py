#!/usr/bin/env python3
"""Regenerate ernesto-klee.md from Chapter*.docx files and push to GitHub Pages."""

import os
import re
import subprocess
import sys
from docx import Document

CHAPTERS_DIR = "/home/mark/projects/TheLeastInterestingCaseOfErnestoKlee"
SITE_DIR = "/home/mark/projects/MarkStringer.github.io"
OUTPUT_FILE = os.path.join(SITE_DIR, "ernesto-klee.md")

PREAMBLE = """\
---
layout: default
title: The Least Interesting Case of Ernesto Klee
---

# The Least Interesting Case of Ernesto Klee

<img src="/assets/ErnestKlee_BookCover_half.jpg" alt="The Least Interesting Case of Ernesto Klee — book cover" width="900" height="1350" style="max-width:100%;height:auto;" />

It had crossed his mind that being a security guard might be an easier life than being a murder detective.

But after a break-in on his first day, things aren't going too well.

Someone has stolen something from Ernesto Klee - the trouble is, he's not sure exactly what.

And he can't call the police, because he's fairly sure they are trying to kill him. His wife isn't talking to him - mainly because of the whole police trying to kill him thing.

Worse still, his daughter is still talking to him, and she's telling him things that no father wants to hear.

A novel written in May 2026, one chapter at a time, every weekday morning.

---"""


def chapter_sort_key(filename):
    m = re.match(r'Chapter (\d+(?:\.\d+)?)', filename)
    return (float(m.group(1)), filename) if m else (float('inf'), filename)


def chapter_anchor(num_str):
    return 'chapter-' + num_str.replace('.', '-')


def parse_filename(filename):
    """Return (num_str, subtitle, heading_text) or (None, None, None)."""
    m = re.match(r'Chapter (\d+(?:\.\d+)?) - (.+?)\.docx$', filename)
    if not m:
        return None, None, None
    num_str = m.group(1)
    subtitle = m.group(2)
    heading_text = f"Chapter {num_str} — {subtitle}"
    return num_str, subtitle, heading_text


def is_title_para(text, subtitle):
    """True if this paragraph is a chapter title label rather than story content."""
    t = text.strip()
    if t.lower().startswith('chapter '):
        return True
    clean = re.sub(r'[^\w\s]', '', t).strip().lower()
    return clean == subtitle.strip().lower()


def extract_content(path, subtitle):
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs]
    non_empty = [p for p in paras if p.strip()]
    if non_empty and is_title_para(non_empty[0], subtitle):
        non_empty = non_empty[1:]
    return '\n\n'.join(non_empty)


def main():
    files = sorted(
        [f for f in os.listdir(CHAPTERS_DIR)
         if f.startswith('Chapter') and f.endswith('.docx')],
        key=chapter_sort_key
    )

    if not files:
        print("No Chapter*.docx files found.", file=sys.stderr)
        sys.exit(1)

    seen = {}
    for f in files:
        num, _, _ = parse_filename(f)
        if num:
            seen.setdefault(num, []).append(f)
    for num, dupes in seen.items():
        if len(dupes) > 1:
            print(f"Warning: multiple files for Chapter {num}: {dupes}")

    sections = []
    for i, filename in enumerate(files):
        num_str, subtitle, heading_text = parse_filename(filename)
        if not heading_text:
            print(f"Skipping unrecognized: {filename}")
            continue

        path = os.path.join(CHAPTERS_DIR, filename)
        content = extract_content(path, subtitle)
        print(f"  {filename}")

        if i == 0:
            section = f"## {heading_text}\n\n{content}"
        else:
            anchor = chapter_anchor(num_str)
            section = f'---\n\n<a id="{anchor}"></a>\n\n## {heading_text}\n\n{content}'

        sections.append(section)

    output = '\n\n'.join([PREAMBLE] + sections) + '\n'

    with open(OUTPUT_FILE, 'w') as f:
        f.write(output)
    print(f"\nWritten: {OUTPUT_FILE}")

    subprocess.run(['git', 'add', 'ernesto-klee.md'], cwd=SITE_DIR, check=True)

    result = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=SITE_DIR)
    if result.returncode == 0:
        print("No changes to publish.")
        return

    last_heading_lines = [l for l in sections[-1].split('\n') if l.startswith('## ')]
    last_heading = last_heading_lines[-1][3:] if last_heading_lines else 'latest'
    msg = f"Publish {len(sections)} chapters — up to {last_heading}"
    subprocess.run(['git', 'commit', '-m', msg], cwd=SITE_DIR, check=True)
    subprocess.run(['git', 'push'], cwd=SITE_DIR, check=True)
    print("Published to GitHub Pages.")


if __name__ == '__main__':
    main()
