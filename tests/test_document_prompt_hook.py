import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from hooks.document_prompt import GUIDANCE, document_context  # noqa: E402
from lib.routing import load_config  # noqa: E402


class DocumentPromptHookTest(unittest.TestCase):
    def test_approved_guidance_matches_route_configuration(self):
        routes = {route['id']: route for route in load_config()['routes']}
        for route_id, paths in GUIDANCE.items():
            route = routes[route_id]
            selected = set(route['policies'])
            if route['module']:
                selected.add(route['module'])
            self.assertEqual(set(paths), selected)

    def test_document_routes_include_real_guidance(self):
        cases = (
            ('Translate this PDF paper into Korean', ('Research.md', 'Evidence.md', 'FileHandling.md')),
            ('Proofread this Korean paragraph', ('Writing.md', 'FileHandling.md')),
            ('Edit the table in existing HWPX document', ('FileHandling.md',)),
        )
        for prompt, names in cases:
            with self.subTest(prompt=prompt):
                context = document_context(prompt)
                self.assertEqual(context['hookSpecificOutput']['hookEventName'], 'UserPromptSubmit')
                for name in names:
                    self.assertIn(name, context['hookSpecificOutput']['additionalContext'])
                self.assertNotIn(prompt, json.dumps(context))

    def test_existing_risky_and_ambiguous_requests_receive_no_context(self):
        for prompt in ('fix code in PDF parser', 'security review of HWPX document',
                       '고객 PDF 논문 번역해줘', 'Translate PDF paper and edit HWPX document',
                       '기존 HWPX 문서의 표를 수정해줘. 문서 파일은 아직 제공되지 않았어.',
                       'What is a PDF?', '', None):
            with self.subTest(prompt=prompt):
                self.assertIsNone(document_context(prompt))

    def test_missing_guidance_reports_failure_without_partial_text(self):
        with tempfile.TemporaryDirectory() as directory:
            result = document_context('Proofread this Korean paragraph', root=Path(directory))
            self.assertIn('systemMessage', result)
            self.assertNotIn('hookSpecificOutput', result)

    def test_guidance_symlink_cannot_escape_plugin_root(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'plugin'
            policies = root / 'policies'
            policies.mkdir(parents=True)
            outside = base / 'outside.md'
            outside.write_text('PRIVATE_SENTINEL', encoding='utf-8')
            try:
                (policies / 'Writing.md').symlink_to(outside)
            except OSError as exc:
                self.skipTest(f'symlink unavailable: {exc}')
            result = document_context('Proofread this Korean paragraph', root=root)
            self.assertIn('systemMessage', result)
            self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))

    def test_cli_emits_context_from_an_unrelated_working_directory(self):
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        with tempfile.TemporaryDirectory() as directory:
            for script in (ROOT / 'scripts/hooks/document_prompt.py',
                           ROOT / 'plugins/taskforge-for-claude/scripts/hooks/document_prompt.py'):
                with self.subTest(script=script):
                    result = subprocess.run(
                        [sys.executable, str(script)],
                        input=json.dumps({'prompt': 'Proofread this Korean paragraph'}),
                        text=True, capture_output=True, cwd=directory, env=env, timeout=90,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('policies/Writing.md', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])

    def test_invalid_input_reports_failure_without_echoing_input(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/hooks/document_prompt.py')],
            input='PRIVATE_MARKER {', text=True, capture_output=True, timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('systemMessage', json.loads(result.stdout))
        self.assertNotIn('PRIVATE_MARKER', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
