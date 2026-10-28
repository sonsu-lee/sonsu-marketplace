#!/usr/bin/env python3
"""Evaluate TypeScript simplifications against immutable external contracts.

Model-generated JavaScript is executed locally in temporary directories. This is
not a sandbox: run only with approval to execute the model's output.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile

import check_activation as ca
import check_plugins as cp
import compare_skill

ROOT = ca.REPO
CASES = ROOT / 'evals/simplify-code/cases'
TOOLCHAIN = ROOT / 'evals/simplify-code/toolchain'
TSC = TOOLCHAIN / 'node_modules/typescript/bin/tsc'


def load_case(name: str) -> tuple[Path, dict]:
    if name not in {f'TS{i:02}' for i in range(1, 7)}:
        raise ValueError(f'unknown case: {name}')
    root = CASES / name
    data = json.loads((root / 'case.json').read_text(), object_pairs_hook=ca._spec_object)
    if (not isinstance(data, dict) or data.get('id') != name or
        not isinstance(data.get('prompt'), str) or not data['prompt'] or
        not isinstance(data.get('editable'), list) or not data['editable'] or
        not isinstance(data.get('criteria'), list) or not data['criteria'] or
        not all(isinstance(x, str) and x for x in data['criteria'])):
        raise ValueError(f'invalid case metadata: {name}')
    for item in data['editable']:
        safe_path(item)
    if len(set(data['editable'])) != len(data['editable']):
        raise ValueError('duplicate editable paths')
    return root, data


def safe_path(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError('file path must be a string')
    p = PurePosixPath(value)
    if (not value or '\\' in value or p.is_absolute() or str(p) != value or
        any(part in ('.', '..') for part in p.parts) or
        not value.startswith('src/') or not value.endswith('.ts')):
        raise ValueError(f'unsafe editable path: {value!r}')
    return value


def parse_submission(text: str, editable: list[str]) -> dict[str, str]:
    try:
        value = json.loads(text, object_pairs_hook=ca._spec_object)
    except json.JSONDecodeError:
        blocks = re.findall(r'^```json[ \t]*\n(.*?)^```[ \t]*$', text, re.M | re.S)
        if len(blocks) != 1 or len(re.findall(r'^```', text, re.M)) != 2:
            raise ValueError('answer must contain one unambiguous JSON submission')
        value = json.loads(blocks[0], object_pairs_hook=ca._spec_object)
    if not isinstance(value, dict) or set(value) != set(editable):
        raise ValueError('answer must map exactly the editable paths to source text')
    for path, content in value.items():
        safe_path(path)
        if not isinstance(content, str):
            raise ValueError(f'{path}: source must be a string')
    return value


def read_overlay(directory: Path, editable: list[str], *, complete: bool) -> dict[str, str]:
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError(f'not a source directory: {directory}')
    result = {}
    for path in directory.rglob('*'):
        if path.is_symlink():
            raise ValueError(f'symlinks forbidden: {path}')
        if path.is_file():
            rel = path.relative_to(directory).as_posix()
            if rel not in editable:
                raise ValueError(f'file outside editable allowlist: {rel}')
            result[rel] = path.read_text(encoding='utf-8')
    if not result or (complete and set(result) != set(editable)):
        raise ValueError('source must contain all editable files' if complete else 'empty overlay')
    return result


def run_process(args: list[str], cwd: Path, home: Path, timeout: int = 60) -> dict:
    try:
        proc = subprocess.run(args, cwd=cwd, env=cp.base_env(home), capture_output=True,
                              text=True, timeout=timeout)
        if proc.returncode < 0:
            raise ValueError(f'check terminated by signal {-proc.returncode}: {args[0]}')
        return {'exit': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f'check timed out after {timeout}s: {args[0]}') from exc


def verify(case_root: Path, data: dict, overlay: dict[str, str]) -> dict:
    if not TSC.is_file():
        raise ValueError(f'missing TypeScript toolchain; run npm ci --prefix {TOOLCHAIN}')
    with tempfile.TemporaryDirectory(prefix='simplification-contract-') as tmp:
        work = Path(tmp) / 'project'
        shutil.copytree(case_root / 'fixture', work, symlinks=False)
        shutil.copytree(case_root / 'checks', work / 'checks', symlinks=False)
        home = Path(tmp) / 'home'
        home.mkdir()
        escapes = []
        for rel, content in overlay.items():
            safe_path(rel)
            if rel not in data['editable']:
                raise ValueError(f'file outside editable allowlist: {rel}')
            target = work / rel
            if not target.is_file() or target.is_symlink():
                raise ValueError(f'fixture missing editable file: {rel}')
            original = Path(tmp) / 'original.ts'
            original.write_text(target.read_text(encoding='utf-8'), encoding='utf-8')
            target.write_text(content, encoding='utf-8')
            check = run_process(['node', str(TOOLCHAIN / 'escapes.mjs'), str(original), str(target)], work, home)
            if check['exit'] != 0:
                raise ValueError(f"escape checker failed: {check['stderr']}")
            escapes.extend(f'{rel}: {line}' for line in check['stdout'].splitlines())
        types = run_process(['node', str(TSC), '--project', 'tsconfig.json'], work, home)
        runtime = (run_process(['node', 'checks/behavior.mjs'], work, home)
                   if types['exit'] == 0 else None)
        return {'escape_violations': escapes, 'types': types, 'runtime': runtime,
                'contract_pass': not escapes and types['exit'] == 0 and runtime is not None and runtime['exit'] == 0,
                'improvement': 'requires_review', 'criteria': data['criteria']}


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def selfcheck(names: list[str]) -> int:
    failed = False
    for name in names:
        root, data = load_case(name)
        initial = verify(root, data, {})
        reference = verify(root, data, read_overlay(root / 'solutions/reference', data['editable'], complete=False))
        mutants = {}
        for mutant in sorted((root / 'mutants').iterdir()):
            if mutant.is_dir():
                mutants[mutant.name] = verify(root, data, read_overlay(mutant, data['editable'], complete=False))
        ok = reference['contract_pass'] and bool(mutants) and all(not r['contract_pass'] for r in mutants.values())
        failed |= not ok
        print(json.dumps({'case': name, 'initial': initial, 'reference': reference,
                          'mutants': mutants, 'selfcheck_pass': ok}, ensure_ascii=False))
    return int(failed)


def observed_read(stdout: str, path: Path) -> bool:
    # A requested read is not proof that the full candidate reached the model.
    wanted = cp.squash(cp.skill_body(path.read_text(encoding='utf-8')))
    requested_ids = set()
    for event in ca.events(stdout):
        msg = event.get('message', {})
        if event.get('type') == 'message_end' and msg.get('role') == 'assistant':
            for block in msg.get('content', []):
                args = block.get('arguments') or {}
                if block.get('type') != 'toolCall' or block.get('name') != 'read':
                    continue
                requested = args.get('path') if isinstance(args, dict) else None
                if isinstance(requested, str) and (requested == str(path) or
                                                  requested.startswith(str(path) + ':')):
                    requested_ids.add(block.get('id'))
        if (event.get('type') != 'message_end' or msg.get('role') != 'toolResult' or
            msg.get('toolCallId') not in requested_ids or msg.get('isError')):
            continue
        returned = '\n'.join(block.get('text', '') for block in msg.get('content', [])
                             if block.get('type') == 'text')
        returned = re.sub(r'^\d+:', '', returned, flags=re.M)
        if wanted and wanted in cp.squash(returned):
            return True
    return False


def model_run(names: list[str], args: argparse.Namespace) -> int:
    candidate = args.candidate.resolve() if args.candidate else None
    if candidate and (candidate.name != 'SKILL.md' or not candidate.is_file()):
        raise ValueError('--candidate must name an existing SKILL.md')
    output = args.output.resolve()
    if candidate and (output.is_relative_to(candidate.parent) or
                      candidate.parent.is_relative_to(output)):
        raise ValueError('candidate directory and output must not overlap')
    if candidate and Path(tempfile.gettempdir()).resolve().is_relative_to(candidate.parent):
        raise ValueError('candidate directory must not contain the temporary workspace root')
    base = args.homes.resolve()
    home, target = ca.homes_for(base, 'omp')
    if not home.is_dir() or not target.is_dir():
        raise ValueError('dedicated omp home and target required; prepare with check_activation.py')
    # Installed copies can silently contaminate the baseline, even when not requested.
    if any(home.rglob('skills/simplify-code/SKILL.md')):
        raise ValueError('omp home contains discoverable simplify-code; use an uncontaminated dedicated home')
    if not ca.has_login('omp', base):
        raise ValueError('omp model login missing in dedicated home')
    pin = ca.load_pins(ROOT, args.profile)['omp']
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for name in names:
        root, data = load_case(name)
        originals = {p: (root / 'fixture' / p).read_text(encoding='utf-8') for p in data['editable']}
        for rep in range(1, args.reps + 1):
            sides = ('baseline', 'candidate') if rep % 2 else ('candidate', 'baseline')
            for side in (sides if candidate else ('baseline',)):
                dest = output / name / f'{rep:03}' / side
                dest.mkdir(parents=True)
                save_json(dest / 'originals.json', originals)
                with tempfile.TemporaryDirectory(prefix='simplification-model-') as tmp:
                    work = Path(tmp) / 'target'
                    shutil.copytree(root / 'fixture', work)
                    skill = None
                    if side == 'candidate':
                        skill = Path(tmp) / 'skills' / 'simplify-code'
                        shutil.copytree(candidate.parent, skill, symlinks=False)
                        shutil.copytree(skill, dest / 'candidate-skill')
                    prompt = data['prompt'] + '\n\nReturn one JSON object, plain or in a single json code fence, mapping every editable path to its complete replacement source text. Editable paths: ' + json.dumps(data['editable']) + '. Do not write files.'
                    if skill:
                        prompt = f'Read and follow {skill / "SKILL.md"} first.\n\n' + prompt
                    proc, trace = ca.execute('omp', base, ROOT, pin, prompt, work, '', '')
                    (dest / 'trace.jsonl').write_text(proc.stdout, encoding='utf-8')
                    (dest / 'stderr.txt').write_text(proc.stderr, encoding='utf-8')
                    text, stop = compare_skill.final_text(proc.stdout)
                    (dest / 'answer.txt').write_text(text, encoding='utf-8')
                    record = {'case': name, 'rep': rep, 'side': side, 'model': pin.model,
                              'effort': pin.effort, 'observed_model': trace.model,
                              'observed_effort': trace.effort, 'candidate_loaded': observed_read(proc.stdout, skill / 'SKILL.md') if skill else None,
                              'error': '', 'contract': None}
                    if proc.returncode != 0 or trace.failed or trace.refused or not trace.reached or stop != 'stop' or trace.writes:
                        record['error'] = trace.error or trace.refused or 'model failed, did not finish, or attempted a write'
                    elif skill and not record['candidate_loaded']:
                        record['error'] = 'candidate SKILL.md read not observed'
                    else:
                        try:
                            submitted = parse_submission(text, data['editable'])
                            save_json(dest / 'submitted.json', submitted)
                            diff = ''.join(''.join(difflib.unified_diff(originals[p].splitlines(True), submitted[p].splitlines(True), fromfile='original/' + p, tofile='submitted/' + p)) for p in data['editable'])
                            (dest / 'changes.diff').write_text(diff, encoding='utf-8')
                            record['contract'] = verify(root, data, submitted)
                        except (ValueError, OSError) as exc:
                            record['error'] = str(exc)
                    save_json(dest / 'result.json', record)
                    results.append(record)
    save_json(output / 'results.json', results)
    print(f'Results: {output}; contract passes require separate improvement review.')
    if any(r['error'] for r in results):
        return 2
    return int(any(not r['contract']['contract_pass'] for r in results))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('selfcheck')
    check.add_argument('--case')
    verification = sub.add_parser('verify')
    verification.add_argument('--case', required=True)
    verification.add_argument('--source', required=True, type=Path)
    run = sub.add_parser('run')
    run.add_argument('--case')
    run.add_argument('--reps', type=int, default=3)
    run.add_argument('--candidate', type=Path)
    run.add_argument('--homes', type=Path, default=ca.DEFAULT_HOMES)
    run.add_argument('--profile', default='default')
    run.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'verify':
            root, data = load_case(args.case)
            result = verify(root, data, read_overlay(args.source, data['editable'], complete=True))
            print(json.dumps(result, indent=2))
            return 0 if result['contract_pass'] else 1
        names = [args.case] if args.case else [f'TS{i:02}' for i in range(1, 7)]
        for name in names:
            load_case(name)
        if args.command == 'selfcheck':
            return selfcheck(names)
        if args.reps < 1:
            raise ValueError('--reps must be positive')
        print('Warning: generated code executes locally; this is not a sandbox.', file=sys.stderr)
        return model_run(names, args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'blocked: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
