#!/usr/bin/env python3
"""Fence-aware Markdown ## section helpers shared by measure_load and validate."""
from __future__ import annotations

import re
from typing import Iterator

HEADING_RE = re.compile(r"(?m)^(#{2})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"(?m)^(`{3,}|~{3,})")


def _masked_for_headings(text: str) -> str:
    """Return a copy of text with fenced code block interiors blanked (newlines kept).

    Headings inside ``` / ~~~ fences are ignored so outline examples do not
    create false section boundaries.
    """
    chars = list(text)
    i = 0
    n = len(text)
    while i < n:
        line_end = text.find("\n", i)
        if line_end < 0:
            line_end = n
        line = text[i:line_end]
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)[0]
            fence_len = len(fence.group(1))
            j = line_end + 1
            while j < n:
                next_end = text.find("\n", j)
                if next_end < 0:
                    next_end = n
                next_line = text[j:next_end]
                close = FENCE_RE.match(next_line)
                if close and close.group(1)[0] == marker and len(close.group(1)) >= fence_len:
                    j = next_end + 1 if next_end < n else n
                    break
                # Blank interior but preserve newlines so line offsets stay aligned.
                for k in range(j, next_end):
                    chars[k] = " "
                j = next_end + 1 if next_end < n else n
            i = j
            continue
        i = line_end + 1 if line_end < n else n
    return "".join(chars)


def iter_h2_spans(text: str) -> Iterator[tuple[str, int, int]]:
    """Yield (title, start, end) for each top-level ## section outside fences.

    ``start`` points at the leading ``##``; ``end`` is exclusive through the
    line before the next real ## or EOF. Intro before the first ## is not yielded.
    """
    masked = _masked_for_headings(text)
    matches = list(HEADING_RE.finditer(masked))
    for index, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        yield title, start, end


def parse_sections(text: str) -> dict[str, str]:
    """Return {title: section_text} including a ``__intro__`` key when present."""
    sections: dict[str, str] = {}
    spans = list(iter_h2_spans(text))
    first = spans[0][1] if spans else len(text)
    sections["__intro__"] = text[:first]
    for title, start, end in spans:
        sections[title] = text[start:end]
    return sections


def section_body(text: str, heading: str) -> str:
    """Return the body of a fence-aware ## section (without the heading line)."""
    for title, start, end in iter_h2_spans(text):
        if title == heading:
            body = text[start:end]
            _, _, rest = body.partition("\n")
            return rest.strip()
    return ""


def section_bytes(text: str, heading: str, *, include_intro: bool = True) -> int:
    """UTF-8 byte size of one section, optionally plus the document intro."""
    sections = parse_sections(text)
    if heading not in sections:
        raise ValueError(f"missing section {heading!r}")
    total = len(sections[heading].encode("utf-8"))
    if include_intro:
        total += len(sections.get("__intro__", "").encode("utf-8"))
    return total
