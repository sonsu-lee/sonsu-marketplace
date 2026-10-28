"""Exercise the submission and contract boundaries without a model."""
from argparse import Namespace
import json
from pathlib import Path
import sys
import tempfile
import unittest
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evaluate_simplification as evaluation


class SubmissionTests(unittest.TestCase):
    def test_exact_mapping_required(self):
        editable = ['src/a.ts', 'src/b.ts']
        self.assertEqual(evaluation.parse_submission('{"src/a.ts":"a","src/b.ts":"b"}', editable),
                         {'src/a.ts': 'a', 'src/b.ts': 'b'})
        for text in ('{"src/a.ts":"a"}', '{"src/a.ts":"a","src/b.ts":1}',
                     '{"src/a.ts":"a","src/a.ts":"b","src/b.ts":"b"}',
                     '{"src/a.ts":"a","src/b.ts":"b","checks/type-contract.ts":""}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                evaluation.parse_submission(text, editable)

    def test_fenced_submission_is_unambiguous(self):
        answer = '{"src/a.ts":"export const value = 1;"}'
        fenced = f'Kept the public contract.\n\n```json\n{answer}\n```\n'
        self.assertEqual(evaluation.parse_submission(fenced, ['src/a.ts']),
                         {'src/a.ts': 'export const value = 1;'})
        for invalid in (fenced + fenced, fenced + '\n```ts\nother code\n```',
                        'Here is JSON: ' + answer):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                evaluation.parse_submission(invalid, ['src/a.ts'])

    def test_overlapping_candidate_output_is_rejected_before_model_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / 'candidate'
            skill.mkdir()
            candidate = skill / 'SKILL.md'
            candidate.write_text('candidate')
            for output in (skill, skill / 'results', root):
                with self.subTest(output=output), self.assertRaises(ValueError):
                    evaluation.model_run(['TS01'], Namespace(candidate=candidate, output=output))
            self.assertFalse((skill / 'results').exists())

    def test_paths_cannot_escape(self):
        for path in ('../src/a.ts', 'src/../a.ts', '/src/a.ts', 'src//a.ts', 'src\\a.ts'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                evaluation.safe_path(path)

    def test_overlay_rejects_extra_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src/a.ts').write_text('a')
            self.assertEqual(evaluation.read_overlay(root, ['src/a.ts'], complete=True), {'src/a.ts': 'a'})
            (root / 'extra').write_text('x')
            with self.assertRaises(ValueError):
                evaluation.read_overlay(root, ['src/a.ts'], complete=True)
            (root / 'extra').unlink()
            (root / 'src/link.ts').symlink_to(root / 'src/a.ts')
            with self.assertRaises(ValueError):
                evaluation.read_overlay(root, ['src/a.ts', 'src/link.ts'], complete=True)

    def test_candidate_exposure_requires_successful_complete_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'SKILL.md'
            path.write_text('# Candidate\n\nPreserve outputs.\nInspect callers.\n')
            request = {'type': 'message_end', 'message': {'role': 'assistant', 'content': [
                {'type': 'toolCall', 'id': 'read-1', 'name': 'read',
                 'arguments': {'path': str(path)}}]}}
            complete = '1:# Candidate\n2:\n3:Preserve outputs.\n4:Inspect callers.'
            self.assertFalse(evaluation.observed_read(json.dumps(request), path))
            for content, failed, call_id, expected in [
                (complete, False, 'read-1', True),
                (complete, True, 'read-1', False),
                ('1:# Candidate', False, 'read-1', False),
                (complete, False, 'another-read', False),
            ]:
                with self.subTest(failed=failed, call_id=call_id, content=content):
                    response = {'type': 'message_end', 'message': {
                        'role': 'toolResult', 'toolCallId': call_id, 'isError': failed,
                        'content': [{'type': 'text', 'text': content}]}}
                    trace = json.dumps(request) + '\n' + json.dumps(response)
                    self.assertEqual(evaluation.observed_read(trace, path), expected)

    def test_timeout_is_incomplete_not_a_contract_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                evaluation.run_process(
                    [sys.executable, '-c', 'import time; time.sleep(5)'], root, root, timeout=0.05)
            failure = evaluation.run_process(
                [sys.executable, '-c', 'raise SystemExit(1)'], root, root)
            self.assertEqual(failure['exit'], 1)

    @unittest.skipUnless(evaluation.TSC.is_file(), 'install the pinned TS toolchain')
    def test_boundary_assertion_is_reviewed_but_suppression_fails(self):
        root, data = evaluation.load_case('TS05')
        source = '''export type Config = { host: string; port: number };
export function parseConfig(json: string): Config {
  const value: unknown = JSON.parse(json);
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw new Error("invalid config");
  const { host, port } = value as Record<string, unknown>;
  if (typeof host !== "string" || typeof port !== "number" || !Number.isInteger(port) || port < 1 || port > 65535) throw new Error("invalid config");
  return { host, port };
}
'''
        result = evaluation.verify(root, data, {'src/config.ts': source})
        self.assertTrue(result['contract_pass'])
        self.assertEqual(result['improvement'], 'requires_review')
        suppressed = evaluation.verify(root, data, {'src/config.ts': '// @ts-nocheck\n' + source})
        self.assertFalse(suppressed['contract_pass'])

    @unittest.skipUnless(evaluation.TSC.is_file(), 'install the pinned TS toolchain')
    def test_escape_checks_distinguish_const_inference_and_suppression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original, submitted = root / 'original.ts', root / 'submitted.ts'
            original.write_text('export const value = "ready";')
            cases = [
                ('export const value = "ready" as const;', []),
                ('export const value = <const>"ready";', []),
                ('export const value = <unknown>"ready";', ['TypeAssertionExpression']),
                ('export const value = "@ts-nocheck";', []),
                ('// @ts-nocheck\nexport const value: number = "ready";', ['@ts-nocheck']),
                ('export const value = "ready" as unknown;', ['AsExpression']),
                ('export const value: any = "ready";', ['AnyKeyword']),
            ]
            for source, violations in cases:
                with self.subTest(source=source):
                    submitted.write_text(source)
                    result = subprocess.run(
                        ['node', str(evaluation.TOOLCHAIN / 'escapes.mjs'),
                         str(original), str(submitted)],
                        text=True, capture_output=True, check=True)
                    if violations:
                        for violation in violations:
                            self.assertIn(violation, result.stdout)
                    else:
                        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
