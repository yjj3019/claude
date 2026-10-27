#!/usr/bin/env python3
"""Attach the approved document guidance to matching Claude prompts."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.routing import ROOT, detect, load_config  # noqa: E402

GUIDANCE = {
    'pdf_translation': ('modules/Research.md', 'policies/FileHandling.md', 'policies/Evidence.md'),
    'korean_proofreading': ('policies/Writing.md', 'policies/FileHandling.md'),
    'formatted_document_edit': ('policies/FileHandling.md',),
}


def document_context(prompt, root=ROOT):
    if not isinstance(prompt, str) or not prompt:
        return None
    try:
        route = detect(prompt, load_config())
        paths = GUIDANCE.get(route['task_type']) if route['risk_level'] == 'low' else None
        if not paths:
            return None
        base = root.resolve(strict=True)
        sections = []
        for name in paths:
            path = (base / name).resolve(strict=True)
            if not path.is_relative_to(base) or not path.is_file() or path.stat().st_size > 65536:
                raise ValueError('invalid guidance path')
            sections.append(f'## TaskForge guidance: {name}\n\n{path.read_text(encoding="utf-8")}')
    except (OSError, ValueError, KeyError, TypeError):
        return {'systemMessage': 'TaskForge document guidance could not be loaded; select the required guidance manually.'}
    return {'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit',
                                   'additionalContext': '\n\n'.join(sections)}}


def main():
    try:
        raw = sys.stdin.buffer.read(1048577)
        if len(raw) > 1048576:
            raise ValueError('hook input too large')
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError('invalid hook input')
        result = document_context(payload.get('prompt'))
    except (ValueError, UnicodeDecodeError):
        result = {'systemMessage': 'TaskForge document guidance could not be selected from the hook input.'}
    if result:
        print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
