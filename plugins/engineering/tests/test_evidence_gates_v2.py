"""Behavior tests for managed evidence DAGs, using the public CLI."""
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/evidence-gates.py'

class ManagedGates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'root'
        self.root.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / 'contract.md').write_text('contract one')
        (self.root / 'design.md').write_text('design one')
        self.package = self.base / 'package'
        shutil.copytree(SCRIPT.parent, self.package / 'scripts')
        policies = self.package / 'references'
        policies.mkdir()
        for name in ('code-quality', 'review-criteria', 'javascript-typescript-review'):
            (policies / (name + '.md')).write_text('policy one')
        (policies / 'model-profiles.json').write_text(json.dumps({'roles': {'general_review': {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'count': 5}, 'focused_review': {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'count': 1}, 'red_team': {'model': 'gpt-6-astra', 'effort': 'high', 'count': 1}}}))
        for name in ('skills/using-engineering-skills/references/quality-gates.md', 'skills/using-engineering-skills/references/agent-execution.md', 'references/model-profiles.md', 'skills/requesting-code-review/code-reviewer.md', 'skills/requesting-code-review/red-team-reviewer.md', 'skills/review-quality/SKILL.md', 'skills/requesting-code-review/SKILL.md', 'skills/review-failure-modes/SKILL.md', 'skills/review-maintainability/SKILL.md', 'skills/review-operability/SKILL.md', 'skills/review-overengineering/SKILL.md'):
            target = self.package / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('Active governance fixture: ' + name)
        self.script = self.package / 'scripts/evidence-gates.py'
        self.config = {'schema_version': 2, 'contracts': ['contract.md'], 'units': [self.unit('design')]}
        self.report = self.base / 'report.md'
        self.report.write_text('Concrete review evidence.')

    def unit(self, name, needs=None, review='checks'):
        return {'id': name, 'stage': 'design', 'needs': needs or [],
                'artifact': {'kind': 'documents', 'paths': ['design.md']},
                'checks': [{'id': 'verify', 'argv': [sys.executable, '-c', 'print("checked")']}],
                'review': review}

    def call(self, command, *args, data=None):
        return subprocess.run([sys.executable, str(self.script), '--cwd', str(self.root), command,
                               '--task-id', 'task', *args], input='' if data is None else json.dumps(data),
                              text=True, capture_output=True, env=dict(os.environ, CODEX_THREAD_ID='controller',
                              PYTHONDONTWRITEBYTECODE='1'), timeout=15)

    def ok(self, command, *args, data=None):
        result = self.call(command, *args, data=data)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return json.loads(result.stdout)

    def init(self):
        return self.ok('init', data=self.config)

    def enter(self, unit='design', request='enter-1'):
        return self.ok('enter', '--unit', unit, '--request-id', request)

    def checked(self, unit='design'):
        self.enter(unit, 'enter-' + unit)
        self.ok('run', '--unit', unit, '--check', 'verify')

    def complete(self, unit='design', request='complete-1', data=None):
        return self.ok('complete-unit', '--unit', unit, '--request-id', request, data=data)

    def test_missing_and_cyclic_dependencies_rejected(self):
        self.config['units'][0]['needs'] = ['missing']
        self.assertNotEqual(self.call('init', data=self.config).returncode, 0)
        self.config['units'] = [self.unit('a', ['b']), self.unit('b', ['a'])]
        self.assertNotEqual(self.call('init', data=self.config).returncode, 0)
        self.assertFalse((self.root / '.engineering/gates/tasks/task/state.json').exists())

    def test_dependency_stale_and_idempotent_completion_history(self):
        self.config['units'].append(self.unit('plan', ['design']))
        self.init()
        self.assertNotEqual(self.call('enter', '--unit', 'plan', '--request-id', 'early').returncode, 0)
        self.checked()
        receipt = self.complete()
        self.assertEqual(receipt, self.complete())
        self.assertNotEqual(self.call('complete-unit', '--unit', 'plan', '--request-id', 'complete-1').returncode, 0)
        self.checked('plan')
        self.complete('plan', 'plan-complete')
        (self.root / 'contract.md').write_text('changed contract')
        self.assertEqual(receipt, self.complete())
        status = self.ok('status')
        self.assertEqual(status['units']['design']['status'], 'stale')
        self.assertEqual(status['units']['plan']['status'], 'stale')
        self.assertFalse(status['ready'])

    def test_checks_required_and_package_tamper_is_stale(self):
        self.init()
        self.enter()
        self.assertNotEqual(self.call('complete-unit', '--unit', 'design', '--request-id', 'c').returncode, 0)
        self.ok('run', '--unit', 'design', '--check', 'verify')
        (self.root / 'design.md').write_text('new design')
        self.assertNotEqual(self.call('complete-unit', '--unit', 'design', '--request-id', 'c').returncode, 0)

    def prepare(self, gate='final-review', data=None):
        return self.ok('prepare-review', '--unit', 'design', '--gate', gate, '--package', str(self.report), data=data)

    def record(self, attempt, reviewer, findings=None, gate='final-review', complete=True):
        raw = {'run_id': reviewer + '-run', 'execution': 'complete' if complete else 'incomplete',
               'verdict': 'failed' if findings else 'passed', 'findings': findings or [],
               'observed': {'model': 'unknown', 'effort': 'unknown'}}
        if gate == 'red-team':
            raw['challenge_verdict'] = 'invalidated' if findings else 'survives_challenge'
        return self.call('record-review', '--unit', 'design', '--gate', gate, '--attempt', str(attempt),
                         '--reviewer-id', reviewer, '--report', str(self.report), data=raw)

    def test_missing_reviewers_single_finding_adjudication_and_round_count(self):
        self.config['units'][0]['review'] = 'independent'
        self.init()
        self.checked()
        prepared = self.prepare()
        self.assertEqual(prepared['requested'], {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'reviewers': 5})
        finding = {'id': 'f1', 'title': 'Wrong result', 'location': 'design.md:1', 'evidence': 'contradicts contract', 'impact': 'wrong behavior'}
        self.assertEqual(self.record(1, 'r1', [finding]).returncode, 0)
        self.assertNotEqual(self.call('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '1',
                                     data={'decisions': []}).returncode, 0)
        for n in range(2, 6):
            self.assertEqual(self.record(1, 'r' + str(n)).returncode, 0)
        self.assertNotEqual(self.record(1, 'r5').returncode, 0)
        outcome = self.ok('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '1',
                         data={'decisions': [{'finding': 'r1:f1', 'decision': 'valid', 'blocking': True, 'reason': 'verified', 'evidence': 'contract.md:1'}]})
        self.assertEqual(outcome['outcome'], 'failed')
        status = self.ok('status')['units']['design']
        self.assertEqual(status['review_rounds'], 1)
        self.assertEqual(status['reviewer_invocations'], 5)
        self.assertNotEqual(self.call('complete-unit', '--unit', 'design', '--request-id', 'c').returncode, 0)

    def review_pass(self, attempt=1, gate='final-review', count=5):
        for n in range(count):
            result = self.record(attempt, gate + '-' + str(attempt) + '-' + str(n), gate=gate)
            self.assertEqual(result.returncode, 0, result.stderr)
        return self.ok('adjudicate', '--unit', 'design', '--gate', gate, '--attempt', str(attempt), data={'decisions': []})

    def test_writer_race_same_request_and_conflicting_request(self):
        self.init()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            results = list(pool.map(lambda _: self.call('enter', '--unit', 'design', '--request-id', 'race'), range(2)))
        successful = [json.loads(r.stdout) for r in results if r.returncode == 0]
        self.assertTrue(successful)
        retry = self.enter(request='race')
        self.assertTrue(all(r == retry for r in successful))
        self.assertNotEqual(self.call('enter', '--unit', 'design', '--request-id', 'other').returncode, 0)
        state = json.loads((self.root / '.engineering/gates/tasks/task/state.json').read_text())
        self.assertEqual(len(state['units']['design']['entries']), 1)

    def test_focused_review_links_full_evidence_and_contract_change_blocks_reuse(self):
        self.config['units'][0]['review'] = 'independent'
        self.init()
        self.checked()
        self.prepare()
        self.review_pass()
        (self.root / 'design.md').write_text('focused correction')
        self.ok('run', '--unit', 'design', '--check', 'verify')
        self.assertNotEqual(self.call('prepare-review', '--unit', 'design', '--gate', 'final-review', '--package', str(self.report), data={'scope': 'focused'}).returncode, 0)
        focused = self.prepare(data={'scope': 'focused', 'prior_round': 1, 'impact_assessment': 'Only corrected wording; interface and contract unchanged.'})
        self.assertEqual(focused['requested']['reviewers'], 1)
        self.review_pass(2, count=1)
        self.complete()
        (self.root / 'contract.md').write_text('new contract')
        self.enter(request='reenter')
        self.ok('run', '--unit', 'design', '--check', 'verify')
        result = self.call('prepare-review', '--unit', 'design', '--gate', 'final-review', '--package', str(self.report), data={'scope': 'focused', 'prior_round': 1, 'impact_assessment': 'Claimed same impact'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('prior full evidence', result.stderr)

    def test_round_budget_persists_after_resume_and_repair(self):
        self.config['units'][0]['review'] = 'independent'
        self.init()
        self.checked()
        for attempt in range(1, 6):
            self.assertEqual(self.prepare()['attempt'], attempt)
            self.ok('abandon', '--unit', 'design')
            self.init()
            self.enter(request='resume-' + str(attempt))
        result = self.call('prepare-review', '--unit', 'design', '--gate', 'final-review', '--package', str(self.report))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('rounds exhausted', result.stderr)
        self.assertEqual(self.ok('status')['units']['design']['review_rounds'], 5)

    def test_incomplete_reviewer_and_false_duplicate_do_not_pass(self):
        self.config['units'][0]['review'] = 'independent'
        self.config['units'][0]['review_profiles'] = {'source': 'Explicit user asks one reviewer', 'general_review': {'model': 'gpt-5.6-luna', 'effort': 'high', 'count': 1}}
        self.init()
        self.checked()
        prepared = self.prepare()
        self.assertEqual(prepared['requested']['effort'], 'high')
        self.assertEqual(prepared['requested']['reviewers'], 1)
        self.assertIn('Explicit user', prepared['profile_source'])
        self.assertEqual(self.record(1, 'incomplete', complete=False).returncode, 0)
        self.assertNotEqual(self.call('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '1', data={'decisions': []}).returncode, 0)
        self.ok('abandon', '--unit', 'design')
        self.enter(request='second')
        self.prepare()
        finding = {'id': 'f', 'title': 'Bug', 'location': 'design.md:1', 'evidence': 'contract contradiction', 'impact': 'bad behavior'}
        self.assertEqual(self.record(2, 'fresh', [finding]).returncode, 0)
        self.assertNotEqual(self.call('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '2', data={'decisions': [{'finding': 'fresh:f', 'decision': 'duplicate', 'duplicate_of': 'fresh:f', 'reason': 'same', 'evidence': 'claimed'}]}).returncode, 0)
        self.assertEqual(self.ok('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '2', data={'decisions': [{'finding': 'fresh:f', 'decision': 'dismissed', 'reason': 'Counterexample is covered by contract exception', 'evidence': 'contract.md:1'}]})['outcome'], 'passed')

    def test_redteam_requires_current_normal_review_and_fresh_identity(self):
        self.config['units'][0]['review'] = 'red-team'
        self.init()
        self.checked()
        self.assertNotEqual(self.call('prepare-review', '--unit', 'design', '--gate', 'red-team', '--package', str(self.report)).returncode, 0)
        self.prepare()
        self.review_pass()
        red = self.prepare('red-team')
        self.assertEqual(red['requested'], {'model': 'gpt-6-astra', 'effort': 'high', 'reviewers': 1})
        self.assertNotEqual(self.record(1, 'final-review-1-0', gate='red-team').returncode, 0)
        self.review_pass(1, 'red-team', 1)
        self.complete()
        self.assertTrue(self.ok('status')['ready'])

    def test_policy_and_frozen_report_tamper_invalidates_completion(self):
        self.config['units'][0]['review'] = 'independent'
        self.init()
        self.checked()
        prepared = self.prepare()
        self.review_pass()
        receipt = self.complete()
        self.assertTrue(self.ok('status')['ready'])
        Path(prepared['package']).chmod(0o600)
        Path(prepared['package']).write_text('tampered review input')
        self.assertEqual(self.ok('status')['units']['design']['status'], 'stale')
        self.assertEqual(self.complete(), receipt)
        (self.package / 'references/code-quality.md').write_text('policy changed')
        self.assertFalse(self.ok('status')['ready'])

    def test_accepted_risk_remains_distinct_through_dependencies(self):
        self.config['units'].append(self.unit('plan', ['design']))
        self.init()
        entry = self.enter()
        accepted = self.complete(data={'outcome': 'accepted_risk', 'acceptance': {'human': 'Named owner', 'source': 'user message 42', 'artifact': entry['binding']['artifact'], 'reason': 'Explicitly deferred validation'}})
        self.assertEqual(accepted['outcome'], 'accepted_risk')
        self.checked('plan')
        downstream = self.complete('plan', 'plan-complete')
        self.assertEqual(downstream['outcome'], 'accepted_risk')
        self.assertEqual(downstream['inherited_acceptances'][0]['receipt_id'], 'complete-1')
        status = self.ok('status')
        self.assertTrue(status['complete'])
        self.assertFalse(status['ready'])
        self.assertNotEqual(self.call('close').returncode, 0)
        self.assertEqual(self.ok('close', '--outcome', 'accepted_risk')['closed'], 'accepted_risk')

    def test_workspace_source_manifests_and_explicit_probe_define_snapshot(self):
        impl = self.base / 'implementation'
        impl.mkdir()
        subprocess.run(['git', 'init', '-q', str(impl)], check=True)
        (impl / '.gitignore').write_text('deps/\nprobe.txt\n')
        (impl / 'package.json').write_text('{"dependencies":{}}')
        (impl / 'probe.txt').write_text('dependency version 1')
        (impl / 'source.py').write_text('import dependency')
        (impl / 'deps').mkdir()
        (impl / 'deps/library.py').write_text('value = 1')
        self.config['units'][0].update(stage='implementation', artifact={'kind': 'workspace', 'path': str(impl), 'inputs': ['probe.txt']})
        self.init()
        self.checked()
        self.complete()
        (impl / 'deps/library.py').write_text('value = 2')
        self.assertTrue(self.ok('status')['ready'])
        (impl / 'probe.txt').write_text('dependency version 2')
        self.assertEqual(self.ok('status')['units']['design']['status'], 'stale')
        (impl / 'probe.txt').write_text('dependency version 1')
        self.assertTrue(self.ok('status')['ready'])
        (impl / 'package.json').write_text('{"dependencies":{"library":"2"}}')
        self.assertEqual(self.ok('status')['units']['design']['status'], 'stale')
        self.config['units'].append(dict(self.unit('integration', ['design']), stage='integration', artifact={'kind': 'workspace', 'path': str(impl)}))
        self.assertNotEqual(self.call('revise', data=self.config).returncode, 0)

    def test_cross_task_writer_lease_and_missing_artifact(self):
        self.init()
        self.enter()
        other = subprocess.run([sys.executable, str(self.script), '--cwd', str(self.root), 'init', '--task-id', 'other', '--session-id', 'other-controller'], input=json.dumps(self.config), text=True, capture_output=True)
        self.assertEqual(other.returncode, 0, other.stderr)
        blocked = subprocess.run([sys.executable, str(self.script), '--cwd', str(self.root), 'enter', '--task-id', 'other', '--unit', 'design', '--request-id', 'other-enter'], text=True, capture_output=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn('another managed writer', blocked.stderr)
        self.ok('run', '--unit', 'design', '--check', 'verify')
        self.complete()
        (self.root / 'design.md').unlink()
        self.assertEqual(self.ok('status')['units']['design']['status'], 'stale')

    def test_known_model_mismatch_and_managed_review_freeze(self):
        self.config['units'][0]['review'] = 'independent'
        self.config['units'][0]['review_profiles'] = {'source': 'User asks one reviewer', 'general_review': {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'count': 1}}
        self.init()
        self.checked()
        self.prepare()
        self.assertNotEqual(self.call('run', '--unit', 'design', '--check', 'verify').returncode, 0)
        raw = {'run_id': 'mismatch-run', 'execution': 'complete', 'verdict': 'passed', 'findings': [], 'observed': {'model': 'gpt-6-astra', 'effort': 'high'}}
        self.ok('record-review', '--unit', 'design', '--gate', 'final-review', '--attempt', '1', '--reviewer-id', 'mismatch-reviewer', '--report', str(self.report), data=raw)
        result = self.call('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '1', data={'decisions': []})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('configuration mismatches', result.stderr)

    def test_direct_implementation_at_controller_root_and_deleted_source(self):
        (self.root / 'old.py').write_text('old source')
        subprocess.run(['git', '-C', str(self.root), 'add', 'old.py'], check=True)
        self.config['units'][0].update(stage='implementation', artifact={'kind': 'workspace', 'path': str(self.root)})
        self.init()
        self.checked()
        (self.root / 'old.py').unlink()
        self.ok('run', '--unit', 'design', '--check', 'verify')
        self.complete()
        self.assertTrue(self.ok('status')['ready'])
        (self.root / 'new.py').write_text('import contract')
        self.assertEqual(self.ok('status')['units']['design']['status'], 'stale')

    def test_valid_nonblocking_improvement_does_not_fail(self):
        self.config['units'][0]['review'] = 'independent'
        self.config['units'][0]['review_profiles'] = {'source': 'User asks one reviewer', 'general_review': {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'count': 1}}
        self.init()
        self.checked()
        self.prepare()
        finding = {'id': 'improve', 'title': 'Explain an uncommon term', 'location': 'design.md:1', 'evidence': 'Term is unexplained', 'impact': 'Small readability improvement'}
        self.assertEqual(self.record(1, 'improver', [finding]).returncode, 0)
        incomplete = {'decisions': [{'finding': 'improver:improve', 'decision': 'valid', 'reason': 'Confirmed improvement', 'evidence': 'design.md:1'}]}
        self.assertNotEqual(self.call('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '1', data=incomplete).returncode, 0)
        incomplete['decisions'][0]['blocking'] = False
        result = self.ok('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '1', data=incomplete)
        self.assertEqual(result['outcome'], 'passed')
        self.complete()
        self.assertTrue(self.ok('status')['ready'])

    def test_redteam_raw_challenge_and_root_conclusion_are_separate(self):
        self.config['units'][0]['review'] = 'red-team'
        self.config['units'][0]['review_profiles'] = {'source': 'User asks one general reviewer', 'general_review': {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'count': 1}}
        self.init()
        self.checked()
        self.prepare()
        self.review_pass(count=1)
        self.prepare('red-team')
        finding = {'id': 'challenge', 'title': 'Counterexample', 'location': 'design.md:1', 'evidence': 'Claimed counterexample', 'impact': 'Claimed contract failure'}
        result = self.record(1, 'challenger', [finding], gate='red-team')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['challenge_verdict'], 'invalidated')
        conclusion = self.ok('adjudicate', '--unit', 'design', '--gate', 'red-team', '--attempt', '1', data={'decisions': [{'finding': 'challenger:challenge', 'decision': 'dismissed', 'reason': 'Counterexample violates the explicit precondition', 'evidence': 'contract.md:1'}]})
        self.assertEqual(conclusion['challenge_verdict'], 'survives_challenge')
        state = json.loads((self.root / '.engineering/gates/tasks/task/state.json').read_text())
        self.assertEqual(state['units']['design']['reviews']['red-team'][0]['raw'][0]['challenge_verdict'], 'invalidated')
        self.prepare('red-team')
        raw = {'run_id': 'uncertain-run', 'execution': 'complete', 'verdict': 'passed', 'challenge_verdict': 'inconclusive', 'findings': [], 'observed': {'model': 'unknown', 'effort': 'unknown'}}
        self.ok('record-review', '--unit', 'design', '--gate', 'red-team', '--attempt', '2', '--reviewer-id', 'uncertain', '--report', str(self.report), data=raw)
        result = self.call('adjudicate', '--unit', 'design', '--gate', 'red-team', '--attempt', '2', data={'decisions': []})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('challenge', result.stderr)

    def test_consumed_reviewer_prompt_and_governance_changes_invalidate(self):
        self.init()
        self.checked()
        self.complete()
        for name in ('skills/requesting-code-review/code-reviewer.md', 'skills/requesting-code-review/red-team-reviewer.md', 'skills/using-engineering-skills/references/quality-gates.md', 'skills/using-engineering-skills/references/agent-execution.md', 'references/model-profiles.md'):
            path = self.package / name
            original = path.read_text()
            path.write_text(original + ' Changed review requirement.')
            self.assertEqual(self.ok('status')['units']['design']['status'], 'stale', name)
            path.write_text(original)
            self.assertTrue(self.ok('status')['ready'], name)

    def test_failed_full_review_can_be_repaired_with_focused_resolution(self):
        self.config['units'][0]['review'] = 'independent'
        self.init()
        self.checked()
        full = self.prepare()
        finding = {'id': 'bug', 'title': 'Wrong operation', 'location': 'design.md:1', 'evidence': 'Contradicts operation in contract', 'impact': 'Wrong output'}
        self.assertEqual(self.record(1, 'full-bug-reviewer', [finding]).returncode, 0)
        for n in range(4):
            self.assertEqual(self.record(1, 'full-clean-' + str(n)).returncode, 0)
        self.ok('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '1', data={'decisions': [{'finding': 'full-bug-reviewer:bug', 'decision': 'valid', 'blocking': True, 'reason': 'Reproduced', 'evidence': 'contract.md:1'}]})
        (self.root / 'design.md').write_text('Corrected operation')
        self.ok('run', '--unit', 'design', '--check', 'verify')
        focused = self.prepare(data={'scope': 'focused', 'prior_round': 1, 'impact_assessment': 'Only operation correction; other full-reviewed contract cases unchanged.'})
        self.assertEqual(focused['requested']['reviewers'], 1)
        self.assertTrue(set(full['files']) <= set(focused['files']))
        self.assertEqual(self.record(2, 'focused-fix-reviewer').returncode, 0)
        self.assertNotEqual(self.call('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '2', data={'decisions': []}).returncode, 0)
        repaired = self.ok('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '2', data={'decisions': [], 'resolutions': [{'finding': 'full-bug-reviewer:bug', 'reason': 'Corrected operation now matches contract', 'evidence': 'design.md:1 and verify log'}]})
        self.assertEqual(repaired['outcome'], 'passed')
        self.complete()
        self.assertTrue(self.ok('status')['ready'])
        state = json.loads((self.root / '.engineering/gates/tasks/task/state.json').read_text())
        self.assertEqual(state['units']['design']['reviews']['final-review'][0]['outcome'], 'failed')

    def start_long_check(self, script):
        self.config['units'][0]['checks'][0]['argv'] = [sys.executable, '-c', script]
        self.init()
        self.enter()
        runner = subprocess.Popen([sys.executable, str(self.script), '--cwd', str(self.root), 'run', '--task-id', 'task', '--unit', 'design', '--check', 'verify'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=dict(os.environ, CODEX_THREAD_ID='controller', PYTHONDONTWRITEBYTECODE='1'))
        def cleanup():
            if runner.poll() is None:
                runner.kill()
            runner.communicate(timeout=8)
        self.addCleanup(cleanup)
        return runner

    def wait_for_file(self, path):
        deadline = time.monotonic() + 6
        while not path.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(path.exists(), str(path))

    def recover_interrupted(self):
        deadline = time.monotonic() + 6
        while True:
            result = self.call('abandon', '--unit', 'design')
            if result.returncode == 0 or time.monotonic() >= deadline:
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)
            time.sleep(0.03)

    def test_killed_runner_recovers_only_after_owned_command_exits(self):
        started, done = self.base / 'started', self.base / 'done'
        script = f"import os,time; from pathlib import Path; Path({str(started)!r}).write_text(str(os.getpid())); print('started',flush=True); time.sleep(1.2); Path({str(done)!r}).write_text('done')"
        runner = self.start_long_check(script)
        self.wait_for_file(started)
        runner.kill()
        runner.communicate(timeout=3)
        self.assertNotEqual(self.call('abandon', '--unit', 'design').returncode, 0)
        self.wait_for_file(done)
        status = self.recover_interrupted()
        self.assertFalse(status['units']['design']['entered'])
        self.assertTrue(status['units']['design']['ready_to_enter'])
        self.assertEqual(status['units']['design']['checks']['verify'], 'inconclusive')
        state_path = self.root / '.engineering/gates/tasks/task/state.json'
        state = json.loads(state_path.read_text())
        row = state['units']['design']['checks']['verify'][0]
        self.assertEqual(row['attempt'], 1)
        self.assertEqual(row['execution'], 'incomplete')
        self.assertEqual(row['outcome'], 'inconclusive')
        self.assertIn('invocation', row)
        self.assertIn('recovery', row)
        self.enter(request='after-interruption')
        self.ok('run', '--unit', 'design', '--check', 'verify')
        state = json.loads(state_path.read_text())
        self.assertEqual([r['attempt'] for r in state['units']['design']['checks']['verify']], [1, 2])
        self.complete()
        self.assertTrue(self.ok('status')['ready'])

    def test_live_runner_cannot_be_abandoned(self):
        started = self.base / 'live-started'
        runner = self.start_long_check(f"import time; from pathlib import Path; Path({str(started)!r}).write_text('started'); time.sleep(0.8)")
        self.wait_for_file(started)
        self.assertFalse(self.ok('status')['units']['design']['ready_to_enter'])
        blocked = self.call('abandon', '--unit', 'design')
        self.assertNotEqual(blocked.returncode, 0)
        state = json.loads((self.root / '.engineering/gates/tasks/task/state.json').read_text())
        self.assertEqual(state['units']['design']['checks']['verify'][0]['outcome'], 'pending')
        self.assertIsNotNone(state['units']['design']['owner'])
        stdout, stderr = runner.communicate(timeout=5)
        self.assertEqual(runner.returncode, 0, stderr + stdout)
        self.complete()
        self.assertTrue(self.ok('status')['ready'])

    def test_orphan_descendant_without_inherited_fd_still_blocks_recovery(self):
        started, child_started, child_done = self.base / 'parent-started', self.base / 'child-started', self.base / 'child-done'
        child = f"import time; from pathlib import Path; Path({str(child_started)!r}).write_text('started'); time.sleep(1.2); Path({str(child_done)!r}).write_text('done')"
        script = f"import os,subprocess,sys,time; from pathlib import Path; subprocess.Popen([sys.executable,'-c',{child!r}],close_fds=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); Path({str(started)!r}).write_text(str(os.getpid())); time.sleep(0.25)"
        runner = self.start_long_check(script)
        self.wait_for_file(child_started)
        runner.kill()
        runner.communicate(timeout=3)
        time.sleep(0.3)
        self.assertFalse(child_done.exists())
        self.assertNotEqual(self.call('abandon', '--unit', 'design').returncode, 0)
        self.wait_for_file(child_done)
        self.assertFalse(self.recover_interrupted()['units']['design']['entered'])

    def revised(self):
        config = json.loads(json.dumps(self.config))
        config['revision'] = {'reason': 'Refine the registered contract', 'source': 'Current task instruction'}
        return config

    def test_revise_cannot_remove_failed_check_or_reset_budget(self):
        self.config['units'][0]['checks'][0]['argv'] = [sys.executable, '-c', 'raise SystemExit(1)']
        self.init()
        self.enter()
        self.assertEqual(self.call('run', '--unit', 'design', '--check', 'verify').returncode, 1)
        self.ok('abandon', '--unit', 'design')
        weakened = json.loads(json.dumps(self.config))
        weakened['units'][0]['checks'] = []
        weakened['units'][0]['checks_reason'] = 'No command applies'
        self.assertNotEqual(self.call('revise', data=weakened).returncode, 0)
        weakened['revision'] = {'reason': 'Remove failing check', 'source': 'Controller note'}
        result = self.call('revise', data=weakened)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('check IDs', result.stderr)
        state = json.loads((self.root / '.engineering/gates/tasks/task/state.json').read_text())
        self.assertEqual(state['config'], self.config)
        self.assertEqual(state['units']['design']['checks']['verify'][0]['outcome'], 'failed')
        self.assertEqual(state['units']['design']['checks']['verify'][0]['attempt'], 1)

    def test_revise_cannot_downgrade_failed_independent_review(self):
        self.config['units'][0]['review'] = 'independent'
        self.config['units'][0]['review_profiles'] = {'source': 'User asks one reviewer', 'general_review': {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'count': 1}}
        self.init()
        self.checked()
        self.prepare()
        finding = {'id': 'bug', 'title': 'Contract violation', 'location': 'design.md:1', 'evidence': 'Contradicts contract', 'impact': 'Incorrect behavior'}
        self.assertEqual(self.record(1, 'blocker', [finding]).returncode, 0)
        self.ok('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '1', data={'decisions': [{'finding': 'blocker:bug', 'decision': 'valid', 'blocking': True, 'reason': 'Verified violation', 'evidence': 'contract.md:1'}]})
        self.ok('abandon', '--unit', 'design')
        weakened = json.loads(json.dumps(self.config))
        weakened['units'][0]['review'] = 'checks'
        self.assertNotEqual(self.call('revise', data=weakened).returncode, 0)
        weakened['revision'] = {'reason': 'Skip review', 'source': 'Controller note'}
        result = self.call('revise', data=weakened)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('review policy', result.stderr)
        self.enter(request='unchanged-review-policy')
        self.assertNotEqual(self.call('complete-unit', '--unit', 'design', '--request-id', 'cannot-pass').returncode, 0)

    def test_revise_oracle_correction_requires_provenance_and_preserves_failure(self):
        self.config['units'][0]['checks'][0]['argv'] = [sys.executable, '-c', "assert '"]
        self.init()
        self.enter()
        self.assertEqual(self.call('run', '--unit', 'design', '--check', 'verify').returncode, 1)
        self.ok('abandon', '--unit', 'design')
        corrected = json.loads(json.dumps(self.config))
        corrected['units'][0]['checks'][0]['argv'] = [sys.executable, '-c', "from pathlib import Path; assert Path('design.md').read_text() == 'design one'"]
        self.assertNotEqual(self.call('revise', data=corrected).returncode, 0)
        corrected['revision'] = {'reason': 'Fix the checker syntax while retaining the exact document-content assertion', 'source': 'Existing task instruction to verify design one'}
        status = self.ok('revise', data=corrected)
        self.assertEqual(status['units']['design']['checks']['verify'], 'stale')
        self.enter(request='corrected-oracle')
        self.ok('run', '--unit', 'design', '--check', 'verify')
        self.complete()
        state = json.loads((self.root / '.engineering/gates/tasks/task/state.json').read_text())
        self.assertEqual(state['config']['revision'], corrected['revision'])
        self.assertEqual(state['config_history'], [self.config])
        self.assertEqual([(r['attempt'], r['outcome']) for r in state['units']['design']['checks']['verify']], [(1, 'failed'), (2, 'passed')])

    def test_revise_preserves_contract_dependency_and_artifact_coverage(self):
        (self.root / 'extra.md').write_text('Additional contract and artifact')
        self.config['contracts'].append('extra.md')
        self.config['units'][0]['artifact']['paths'].append('extra.md')
        self.config['units'].append(self.unit('plan', ['design']))
        self.init()
        reductions = []
        config = self.revised()
        config['contracts'].remove('extra.md')
        reductions.append((config, 'contract coverage'))
        config = self.revised()
        config['units'][1]['needs'] = []
        reductions.append((config, 'dependency coverage'))
        config = self.revised()
        config['units'][0]['artifact']['paths'].remove('extra.md')
        reductions.append((config, 'artifact coverage'))
        for config, diagnostic in reductions:
            result = self.call('revise', data=config)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(diagnostic, result.stderr)
        strengthened = self.revised()
        strengthened['units'][0]['review'] = 'independent'
        self.ok('revise', data=strengthened)

    def test_revise_profile_change_needs_explicit_source_and_roles(self):
        self.config['units'][0]['review'] = 'independent'
        self.config['units'][0]['review_profiles'] = {'source': 'User message requiring five reviews', 'general_review': {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'count': 5}}
        self.init()
        stripped = self.revised()
        del stripped['units'][0]['review_profiles']
        result = self.call('revise', data=stripped)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('profile', result.stderr)
        explicit = self.revised()
        explicit['revision'] = {'reason': 'Apply the user-chosen current task review profile', 'source': 'User message changing this task to one review'}
        explicit['units'][0]['review_profiles'] = {'source': explicit['revision']['source'], 'general_review': {'model': 'gpt-5.6-luna', 'effort': 'xhigh', 'count': 1}}
        self.ok('revise', data=explicit)
        self.checked()
        self.assertEqual(self.prepare()['requested']['reviewers'], 1)
        self.assertNotEqual(self.call('complete-unit', '--unit', 'design', '--request-id', 'still-needs-review').returncode, 0)

    def test_older_full_round_cannot_hide_newer_focused_blocking_findings(self):
        self.config['units'][0]['review'] = 'independent'
        self.init()
        self.checked()
        self.prepare()
        self.review_pass()
        (self.root / 'design.md').write_text('First localized correction')
        self.ok('run', '--unit', 'design', '--check', 'verify')
        round_two = self.prepare(data={'scope': 'focused', 'prior_round': 1, 'impact_assessment': 'Localized correction within prior full-reviewed scope'})
        finding = {'id': 'new-bug', 'title': 'New failure', 'location': 'design.md:1', 'evidence': 'The first correction violates the contract', 'impact': 'Wrong result'}
        self.assertEqual(self.record(2, 'second-round-blocker', [finding]).returncode, 0)
        self.ok('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '2', data={'decisions': [{'finding': 'second-round-blocker:new-bug', 'decision': 'valid', 'blocking': True, 'reason': 'Confirmed current failure', 'evidence': 'contract.md:1'}]})
        (self.root / 'design.md').write_text('Second localized correction')
        self.ok('run', '--unit', 'design', '--check', 'verify')
        round_three = self.prepare(data={'scope': 'focused', 'prior_round': 1, 'impact_assessment': 'Fix the newly discovered failure; preserve earlier full-reviewed scope'})
        self.assertEqual(self.record(3, 'third-round-reviewer').returncode, 0)
        result = self.call('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '3', data={'decisions': []})
        self.assertNotEqual(result.returncode, 0)
        self.assertNotEqual(self.call('complete-unit', '--unit', 'design', '--request-id', 'bypass-later-failure').returncode, 0)
        self.assertTrue(set(round_two['files']) <= set(round_three['files']))
        result = self.ok('adjudicate', '--unit', 'design', '--gate', 'final-review', '--attempt', '3', data={'decisions': [], 'resolutions': [{'finding': 'second-round-blocker:new-bug', 'reason': 'Second correction matches the contract', 'evidence': 'design.md:1 and current verify log'}]})
        self.assertEqual(result['outcome'], 'passed')
        self.complete(request='after-explicit-resolution')
        self.assertTrue(self.ok('status')['ready'])

    def test_external_json_objects_fail_cleanly_without_mutation(self):
        malformed = ([], dict(self.config, units=[[]]))
        for config in malformed:
            result = self.call('init', data=config)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)
            self.assertIn('JSON object', result.stderr)
        self.assertFalse((self.root / '.engineering/gates/tasks/task/state.json').exists())
        self.init()
        result = self.call('enter', '--unit', 'design', '--request-id', 'invalid-body', data=[])
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)
        self.assertFalse((self.root / '.engineering/gates/writer.json').exists())

    def test_freeze_failure_releases_unregistered_writer_lease(self):
        import importlib.util
        from types import SimpleNamespace
        from unittest import mock
        self.init()
        def load_module(name, path):
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        gate = load_module('gate_freeze_fixture', self.script)
        managed = load_module('managed_freeze_fixture', self.script.parent / 'evidence_gates_v2.py')
        managed.G = gate
        args = SimpleNamespace(task_id='task', unit='design', request_id='freeze-failure')
        original_freeze = managed.freeze
        def remove_document_then_freeze(*arguments):
            (self.root / 'design.md').unlink()
            return original_freeze(*arguments)
        with gate.lock(self.root):
            state = managed.load(self.root, 'task')
            with mock.patch.object(managed, 'freeze', side_effect=remove_document_then_freeze):
                with self.assertRaises(gate.GateError):
                    managed.enter(self.root, state, args, {})
        self.assertFalse((self.root / '.engineering/gates/writer.json').exists())
        state = json.loads((self.root / '.engineering/gates/tasks/task/state.json').read_text())
        self.assertIsNone(state['units']['design']['owner'])
        self.assertNotIn('freeze-failure', state['requests'])
        (self.root / 'design.md').write_text('design one')
        self.enter(request='after-freeze-failure')

    def test_review_procedure_skill_changes_invalidate_current_completion(self):
        self.init()
        self.checked()
        self.complete()
        for name in ('skills/review-quality/SKILL.md', 'skills/requesting-code-review/SKILL.md', 'skills/review-failure-modes/SKILL.md', 'skills/review-maintainability/SKILL.md', 'skills/review-operability/SKILL.md', 'skills/review-overengineering/SKILL.md'):
            path = self.package / name
            original = path.read_text()
            path.write_text(original + ' Updated active review procedure.')
            self.assertEqual(self.ok('status')['units']['design']['status'], 'stale', name)
            path.write_text(original)
            self.assertTrue(self.ok('status')['ready'])

if __name__ == '__main__':
    unittest.main()
