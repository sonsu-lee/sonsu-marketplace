"""Managed evidence units, not an agent scheduler or a filesystem security boundary.

See evidence-gates.py CLI. All mutations serialize on the controller workspace lock.
A persisted owner excludes other managed writers until completion/abandon. Snapshots
are read-only content packages; arbitrary processes can still edit their source.
Raw reviewer claims, controller adjudication, and current validity stay separate.
"""
from pathlib import Path
import io
from contextlib import contextmanager, ExitStack
import os
import stat
import sys
import subprocess
import tarfile
import tempfile

G = None
POLICIES = ('code-quality', 'review-criteria', 'javascript-typescript-review')
GOVERNANCE = ('references/quality-gates.md',
              'references/agent-execution.md',
              'references/model-profiles.md',
              'references/review/code-reviewer.md',
              'references/review/red-team-reviewer.md',
              'skills/review/SKILL.md',
              'references/independent-review.md',
              'skills/review-failure-modes/SKILL.md',
              'skills/review-maintainability/SKILL.md',
              'skills/review-operability/SKILL.md',
              'skills/review-overengineering/SKILL.md')


def need(value, message):
    G.require(value, message)


def text(value, name):
    need(isinstance(value, str) and value.strip(), 'missing ' + name)
    return value


def read_input():
    data = G.sys.stdin.buffer.read(G.MAX_JSON + 1)
    value = G.parse_json(data) if data.strip() else {}
    need(isinstance(value, dict), 'command input must be a JSON object')
    return value


def validate(config, root, check_inputs=True):
    need(isinstance(config, dict) and {'schema_version', 'contracts', 'units'} <= set(config) <= {'schema_version', 'contracts', 'units', 'revision'} and
         config['schema_version'] == 2, 'invalid v2 configuration')
    if 'revision' in config:
        revision = config['revision']
        need(isinstance(revision, dict) and set(revision) == {'reason', 'source'}, 'invalid revision provenance')
        text(revision['reason'], 'revision reason')
        text(revision['source'], 'revision instruction source')
    need(isinstance(config['contracts'], list) and config['contracts'], 'declare contract inputs')
    for name in config['contracts']:
        G.relative_input(name)
        if check_inputs:
            G.read_file(root / name)
    units = config['units']
    need(isinstance(units, list) and 0 < len(units) <= 128, 'declare 1..128 units')
    need(all(isinstance(u, dict) for u in units), 'each unit must be a JSON object')
    ids = [G.identifier(u.get('id')) for u in units]
    need(len(ids) == len(set(ids)), 'duplicate unit ID')
    workspaces = []
    for u in units:
        need(set(u) <= {'id', 'stage', 'needs', 'artifact', 'checks', 'review', 'checks_reason', 'review_profiles'} and
             {'id', 'stage', 'needs', 'artifact', 'checks', 'review'} <= set(u), 'invalid unit fields')
        need(u['stage'] in ('design', 'plan', 'implementation', 'integration'), 'invalid stage')
        need(isinstance(u['needs'], list) and len(set(u['needs'])) == len(u['needs']) and
             all(n in ids for n in u['needs']), 'missing or duplicate dependency ID')
        need(u['review'] in ('checks', 'independent', 'red-team'), 'invalid review policy')
        overrides = u.get('review_profiles', {})
        need(isinstance(overrides, dict), 'review_profiles must be a JSON object')
        if overrides:
            need(isinstance(overrides, dict) and set(overrides) <= {'source', 'general_review', 'focused_review', 'red_team'}, 'invalid review profile overrides')
            text(overrides.get('source'), 'explicit user profile source')
            for role in set(overrides) - {'source'}:
                profile_validate(overrides[role])
        a = u['artifact']
        need(isinstance(a, dict), 'invalid artifact')
        if a.get('kind') == 'documents':
            need(set(a) == {'kind', 'paths'} and u['stage'] in ('design', 'plan'), 'documents require design or plan stage')
            need(isinstance(a['paths'], list) and a['paths'], 'declare document package paths')
            for name in a['paths']:
                G.relative_input(name)
                if check_inputs:
                    G.read_file(root / name)
        else:
            need({'kind', 'path'} <= set(a) <= {'kind', 'path', 'inputs'} and a['kind'] == 'workspace' and
                 u['stage'] in ('implementation', 'integration'), 'implementation/integration require workspace artifact')
            need(isinstance(a.get('inputs', []), list), 'invalid workspace evidence inputs')
            for name in a.get('inputs', []):
                G.relative_input(name)
            p = G.safe_path(Path(a['path']))
            need(p.is_absolute() and p == p.resolve() and G.workspace(p) == p, 'workspace must be absolute Git root')
            need(p == root or (not p.is_relative_to(root) and not root.is_relative_to(p)), 'workspace must be controller root or an isolated checkout')
            need(all(p != q and not p.is_relative_to(q) and not q.is_relative_to(p) for q in workspaces), 'unit workspaces must be separate')
            workspaces.append(p)
        need(isinstance(u['checks'], list), 'invalid checks')
        if u['checks']:
            G.config_validate({'inputs': config['contracts'], 'checks': u['checks']}, root)
        else:
            need(u['review'] != 'checks', 'checks policy requires at least one check')
            text(u.get('checks_reason'), 'checks_reason for no applicable command')
    seen, active = set(), set()
    by_id = {u['id']: u for u in units}
    def visit(name):
        need(name not in active, 'cyclic unit dependencies')
        if name in seen:
            return
        active.add(name)
        for dep in by_id[name]['needs']:
            visit(dep)
        active.remove(name)
        seen.add(name)
    for name in ids:
        visit(name)
    return config


def validate_revision(state, config):
    """Preserve declared obligations; command equivalence remains a root judgment.

    Provenance records an existing instruction, not a new approval flow or proof
    that a changed oracle is semantically equivalent. Risk acceptance has its own
    explicit outcome and must not be implemented by removing mandatory gates.
    """
    previous = state['config']
    need('revision' in config, 'configuration refinement requires revision reason and instruction source')
    need(set(previous['contracts']) <= set(config['contracts']), 'revise cannot reduce contract coverage')
    by_id = {u['id']: u for u in config['units']}
    rank = {'checks': 0, 'independent': 1, 'red-team': 2}
    for before in previous['units']:
        after = by_id[before['id']]
        required_checks = set(state['units'][before['id']]['checks'])
        need(required_checks <= {c['id'] for c in after['checks']}, 'revise must preserve existing check IDs and their budgets')
        need(rank[after['review']] >= rank[before['review']], 'revise cannot lower the review policy; use explicit accepted_risk')
        need(set(before['needs']) <= set(after['needs']), 'revise cannot reduce dependency coverage')
        need(before['stage'] == after['stage'], 'revise must preserve the registered stage')
        old_artifact, new_artifact = before['artifact'], after['artifact']
        need(old_artifact['kind'] == new_artifact['kind'], 'revise cannot replace artifact coverage kind')
        if old_artifact['kind'] == 'documents':
            need(set(old_artifact['paths']) <= set(new_artifact['paths']), 'revise cannot reduce artifact coverage')
        else:
            need(old_artifact['path'] == new_artifact['path'], 'revise cannot redirect workspace artifact coverage')
            need(set(old_artifact.get('inputs', [])) <= set(new_artifact.get('inputs', [])), 'revise cannot reduce explicit workspace artifact coverage')
        old_profiles, new_profiles = before.get('review_profiles', {}), after.get('review_profiles', {})
        if old_profiles != new_profiles:
            text(new_profiles.get('source'), 'explicit profile decision source')
            need(set(old_profiles) - {'source'} <= set(new_profiles) - {'source'}, 'profile changes must explicitly replace existing role overrides')
            need(new_profiles['source'] == config['revision']['source'], 'profile override must link to the current revision instruction source')


def load(root, task):
    state = G.read_json(G.task_path(root, task))
    need(state.get('schema_version') == 2 and state.get('workspace_root') == str(root) and
         state.get('task_id') == task, 'v2 task identity mismatch; legacy receipts cannot pass v2')
    need(state.get('host', 'codex') in ('codex', 'claude-code'), 'invalid task host')
    validate(state['config'], root, check_inputs=False)
    return state


def definition(state, name):
    return next((u for u in state['config']['units'] if u['id'] == name), None)


def unit(state, name):
    need(name in state['units'], 'unknown unit')
    return state['units'][name]


def cwd(root, u):
    return root if u['artifact']['kind'] == 'documents' else Path(u['artifact']['path'])


def profile_validate(profile):
    need(isinstance(profile, dict) and set(profile) == {'model', 'effort', 'count'}, 'invalid review profile')
    text(profile['model'], 'requested model')
    text(profile['effort'], 'requested effort')
    need(type(profile['count']) is int and 1 <= profile['count'] <= 32, 'review count must be 1..32')
    return profile


def profiles(host):
    package = Path(__file__).resolve().parents[1]
    filename = 'claude-model-profiles.json' if host == 'claude-code' else 'model-profiles.json'
    return G.read_json(package / 'references' / filename)['roles']


def policy_digest(host):
    package = Path(__file__).resolve().parents[1]
    model_reference = 'references/claude-model-profiles.md' if host == 'claude-code' else 'references/model-profiles.md'
    governance = tuple(model_reference if name == 'references/model-profiles.md' else name for name in GOVERNANCE)
    if host == 'claude-code':
        governance += ('references/claude-code-tools.md',)
    profile_file = 'claude-model-profiles.json' if host == 'claude-code' else 'model-profiles.json'
    return G.digest(G.encode({'policies': {name: G.file_digest(package / 'references' / (name + '.md')) for name in POLICIES}, 'profiles': G.file_digest(package / 'references' / profile_file), 'governance': {name: G.file_digest(package / name) for name in governance}}))


def context(root, state, u):
    host = state.get('host', 'codex')
    return {'contract': G.digest(G.encode({p: G.file_digest(root / p) for p in state['config']['contracts']})),
            'policy': policy_digest(host), 'definition': G.digest(G.encode(u)),
            'runtime': G.digest(Path(__file__).read_bytes() + Path(G.__file__).read_bytes()),
            'dependencies': {n: G.digest(G.encode(unit(state, n)['completions'][-1]))
                             if unit(state, n)['completions'] else None for n in u['needs']}}


def files(root, u):
    base = cwd(root, u)
    if u['artifact']['kind'] == 'documents':
        names = u['artifact']['paths']
    else:
        # Source inventory includes imports/configuration across the workspace.
        # Ignored installed dependencies and caches are not an environment image;
        # record relevant environment probes explicitly as check/input evidence.
        names = set(os.fsdecode(n) for n in G.git(base, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').split(b'\0') if n)
        manifests = ('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'package-lock.json',
                     'yarn.lock', 'bun.lock', 'bun.lockb', 'pyproject.toml', 'uv.lock', 'poetry.lock',
                     'requirements.txt', 'Cargo.toml', 'Cargo.lock', 'go.mod', 'go.sum',
                     'Gemfile', 'Gemfile.lock', 'composer.json', 'composer.lock')
        names.update(n for n in manifests if (base / n).exists())
        names.update(u['artifact'].get('inputs', []))
        names = [n for n in names if n != G.STATE_DIR and not n.startswith(G.STATE_DIR + '/')]
    result = []
    for name in sorted(set(names)):
        path = base / name
        G.safe_path(path)
        if not path.exists() and u['artifact']['kind'] == 'workspace' and name not in u['artifact'].get('inputs', []):
            result.append([name, 'deleted', None])
            continue
        need(path.is_file(), 'snapshot input missing or unsupported (source symlinks/submodules are not supported)')
        result.append([name, stat.S_IMODE(path.stat().st_mode), G.file_digest(path)])
    return result


def binding(root, state, u):
    return {'context': context(root, state, u), 'artifact': G.digest(G.encode(files(root, u)))}


def directory(root, state):
    return G.task_path(root, state['task_id']).parent


def valid_files(root, state, row):
    try:
        return all(G.file_digest(directory(root, state) / n) == d for n, d in row.get('files', {}).items())
    except (G.GateError, OSError):
        return False


def current(root, state, row, b):
    return bool(row and row['binding'] == b and valid_files(root, state, row))


def focused_chain(data, prior_round, context_value, before_attempt=None):
    end = before_attempt - 1 if before_attempt is not None else None
    return [r for r in data['reviews']['final-review'][prior_round - 1:end]
            if r['binding']['context'] == context_value and r.get('outcome') in ('passed', 'failed')
            and 'adjudication' in r]


def unresolved_findings(chain):
    unresolved = set()
    for review in chain:
        # A later validated resolution discharges an earlier finding without
        # rewriting that earlier failed receipt. New blockers remain obligations.
        unresolved.difference_update(r['finding'] for r in review['adjudication'].get('resolutions', []))
        unresolved.update(d['finding'] for d in review['adjudication']['decisions']
                          if d['decision'] == 'valid' and d['blocking'])
    return unresolved


def review_current(root, state, row, b):
    if not current(root, state, row, b):
        return False
    if row.get('gate') == 'red-team':
        if row.get('outcome') == 'passed' and row.get('challenge_verdict') != 'survives_challenge':
            return False
        normal = unit(state, row['unit'])['reviews']['final-review']
        if not normal or normal[-1]['outcome'] != 'passed' or not review_current(root, state, normal[-1], b) or row['normal_review'] != G.digest(G.encode(normal[-1])):
            return False
    if row.get('scope') == 'focused':
        history = unit(state, row['unit'])['reviews']['final-review']
        prior = history[row['prior_round'] - 1]
        # Prior full review may concern the previous artifact, but its context and
        # frozen evidence must still match. No contract/dependency/policy reuse.
        return (prior['scope'] == 'full' and prior.get('outcome') in ('passed', 'failed') and 'adjudication' in prior and
                prior['binding']['context'] == b['context'] and valid_files(root, state, prior))
    return True


def evidence(root, state, name, b):
    u, data = definition(state, name), unit(state, name)
    for check in u['checks']:
        rows = data['checks'].get(check['id'], [])
        if not rows or not current(root, state, rows[-1], b) or rows[-1]['outcome'] != 'passed':
            return False
    gates = [] if u['review'] == 'checks' else ['final-review']
    if u['review'] == 'red-team':
        gates.append('red-team')
    for gate in gates:
        rows = data['reviews'][gate]
        if not rows or not review_current(root, state, rows[-1], b) or rows[-1].get('outcome') != 'passed':
            return False
        if gate == 'red-team' and rows[-1]['normal_review'] != G.digest(G.encode(data['reviews']['final-review'][-1])):
            return False
    return True


def inspect(root, state):
    result = {}
    def visit(name):
        if name in result:
            return result[name]
        u, data = definition(state, name), unit(state, name)
        deps = all([visit(n)['status'] in ('passed', 'accepted_risk') for n in u['needs']])
        rows = data['completions']
        b, check_status, review_status = None, {}, {}
        try:
            b = binding(root, state, u)
            for c in u['checks']:
                history = data['checks'].get(c['id'], [])
                check_status[c['id']] = ('not_run' if not history else history[-1]['outcome'] if current(root, state, history[-1], b) else 'stale')
            for gate, history in data['reviews'].items():
                review_status[gate] = ('not_run' if not history else history[-1]['outcome'] if review_current(root, state, history[-1], b) else 'stale')
            fresh = bool(rows and deps and current(root, state, rows[-1], b) and
                         (evidence(root, state, name, b) if 'acceptance' not in rows[-1] else True))
            status = rows[-1]['outcome'] if fresh else ('stale' if rows else 'not_run')
            if not rows:
                values = list(check_status.values()) + list(review_status.values())
                status = next((v for v in ('failed', 'blocked', 'inconclusive', 'stale') if v in values), status)
        except (G.GateError, OSError):
            status, fresh = ('stale' if rows else 'blocked'), False
        if any(rs and rs[-1]['outcome'] == 'pending' for rs in
               list(data['checks'].values()) + list(data['reviews'].values())):
            status = 'pending'
        reviews = [r for rs in data['reviews'].values() for r in rs]
        result[name] = {'status': status, 'stage': u['stage'], 'artifact_digest': b['artifact'] if b else None,
                        'checks': check_status, 'reviews': review_status,
                        'acceptance': rows[-1].get('acceptance') if rows else None,
                        'inherited_acceptances': rows[-1].get('inherited_acceptances', []) if rows else [],
                        'dependencies_ready': deps, 'entered': data['owner'] is not None,
                        'ready_to_enter': deps and not state['closed'] and status != 'passed' and data['owner'] is None,
                        'review_rounds': len(data['reviews']['final-review']),
                        'redteam_rounds': len(data['reviews']['red-team']),
                        'reviewer_invocations': sum(len(r['raw']) for r in reviews),
                        'completion_receipt': rows[-1]['receipt_id'] if rows else None}
        return result[name]
    for u in state['config']['units']:
        visit(u['id'])
    return {'schema_version': 2, 'mode': 'managed-evidence', 'task_id': state['task_id'],
            'ready': all(x['status'] == 'passed' for x in result.values()),
            'complete': all(x['status'] in ('passed', 'accepted_risk') for x in result.values()), 'units': result,
            'closed': state['closed']}


def freeze(root, state, u, label, expected):
    # Archive the entire declared artifact, not merely the diff. Re-read afterward
    # to detect writes during capture. The archive itself is digest checked later.
    name = u['id'] + '-' + label + '.tar'
    path = directory(root, state) / name
    with tempfile.TemporaryFile() as stream:
        with tarfile.open(fileobj=stream, mode='w') as archive:
            for filename, mode, fingerprint in files(root, u):
                if mode == 'deleted':
                    continue
                content = G.read_file(cwd(root, u) / filename)
                need(G.digest(content) == fingerprint, 'artifact changed while freezing')
                info = tarfile.TarInfo(filename)
                info.size, info.mode = len(content), mode & ~0o222
                archive.addfile(info, io.BytesIO(content))
        need(binding(root, state, u) == expected, 'artifact changed while freezing')
        stream.seek(0)
        if path.exists():
            value = G.hashlib.sha256()
            for chunk in iter(lambda: stream.read(65536), b''):
                value.update(chunk)
            need(G.file_digest(path) == 'sha256:' + value.hexdigest(), 'existing snapshot differs; request cannot be retried')
        else:
            G.atomic_chunks(path, iter(lambda: stream.read(65536), b''))
    path.chmod(0o400)
    return {name: G.file_digest(path)}


def save(root, state):
    G.save(root, state)


def initialize(root, args, config):
    validate(config, root)
    session = G.session_identity(args.session_id)
    host = G.host_identity(args.host)
    with G.lock(root):
        path = G.task_path(root, args.task_id)
        pointer = G.session_path(root, session)
        if pointer.exists():
            other = G.read_json(pointer)['task_id']
            if other != args.task_id:
                need(G.read_json(G.task_path(root, other))['closed'], 'session already has active task')
        if path.exists():
            state = load(root, args.task_id)
            need(state.get('host', 'codex') == host, 'task host changed; use the original host')
            need(state['config'] == config, 'configuration changed; use revise, budgets persist')
            need(session not in {r['reviewer_id'] for d in state['units'].values() for rs in d['reviews'].values()
                                 for row in rs for r in row['raw']}, 'controller conflicts with reviewer')
            if session not in state['sessions']:
                state['sessions'].append(session)
            state['closed'] = False
        else:
            state = {'schema_version': 2, 'task_id': args.task_id, 'workspace_root': str(root),
                     'host': host, 'config': config, 'config_history': [], 'sessions': [session], 'closed': False,
                     'requests': {}, 'units': {u['id']: {'owner': None, 'entries': [], 'completions': [],
                       'checks': {c['id']: [] for c in u['checks']}, 'reviews': {'final-review': [], 'red-team': []}}
                       for u in config['units']}}
        # Fail before registration if canonical policy/runtime files unavailable.
        for u in config['units']:
            binding(root, state, u)
        G.exclude_state(root)
        save(root, state)
        G.atomic_write(pointer, G.encode({'task_id': args.task_id}))
        return inspect(root, state)


@contextmanager
def writer_lock(root, u):
    target = cwd(root, u)
    if target == root:
        yield
    else:
        G.exclude_state(target)
        with G.lock(target):
            yield


def writer_path(root, u):
    return G.safe_path(cwd(root, u) / G.STATE_DIR / 'writer.json')


def writer_identity(root, state, u):
    return {'controller': str(root), 'task': state['task_id'], 'unit': u['id']}


def release_writer(root, state, u):
    with writer_lock(root, u):
        path = writer_path(root, u)
        if path.exists():
            need(G.read_json(path) == writer_identity(root, state, u), 'managed writer lease changed')
            path.unlink()


def save_released_writer(root, state, u, was_owned):
    # Persist the receipt and cleared owner before relinquishing exclusivity.
    # If unlink is interrupted, a retry/abandon can remove our residual lease.
    with writer_lock(root, u):
        path = writer_path(root, u)
        ours = path.exists() and G.read_json(path) == writer_identity(root, state, u)
        need(not was_owned or not path.exists() or ours, 'managed writer lease changed')
        save(root, state)
        if ours:
            path.unlink()


def cleanup_released_writer(root, state, u):
    # An old idempotent request must not release a later entry or another task.
    if unit(state, u['id'])['owner'] is None:
        with writer_lock(root, u):
            path = writer_path(root, u)
            if path.exists() and G.read_json(path) == writer_identity(root, state, u):
                path.unlink()


def active(root, state, name):
    need(not state['closed'], 'task is closed')
    u, data = definition(state, name), unit(state, name)
    need(data['owner'] is not None, 'enter unit before managed work')
    need(inspect(root, state)['units'][name]['dependencies_ready'], 'dependency is not currently passed')
    need(data['owner']['context'] == context(root, state, u), 'entry context stale; abandon and enter again')
    need(G.read_json(writer_path(root, u)) == writer_identity(root, state, u), 'managed writer lease missing or changed')
    need(valid_files(root, state, data['entries'][-1]), 'entry snapshot evidence changed')
    return u, data


def remember(state, request, payload, receipt=None):
    G.identifier(request)
    previous = state['requests'].get(request)
    if previous:
        need(previous['payload'] == payload, 'request ID reused with conflicting payload')
        return previous['receipt']
    if receipt is not None:
        state['requests'][request] = {'payload': payload, 'receipt': receipt}
    return None


def enter(root, state, args, body):
    payload = {'command': 'enter', 'unit': args.unit, 'body': body}
    previous = remember(state, args.request_id, payload)
    if previous:
        return previous
    need(not body, 'enter does not accept extra payload')
    u, data = definition(state, args.unit), unit(state, args.unit)
    status = inspect(root, state)['units'][args.unit]
    need(status['ready_to_enter'], 'unit dependencies not passed, already entered/passed, or task closed')
    need(data['owner'] is None, 'unit already has a managed writer')
    # Documents share the controller source workspace; serialize its managed writers.
    for other in state['config']['units']:
        need(not (unit(state, other['id'])['owner'] and cwd(root, other) == cwd(root, u)), 'workspace has a managed writer')
    b = binding(root, state, u)
    with writer_lock(root, u):
        path = writer_path(root, u)
        if path.exists():
            need(G.read_json(path) == writer_identity(root, state, u), 'workspace has another managed writer')
        G.atomic_write(path, G.encode(writer_identity(root, state, u)))
    try:
        row = {'receipt_id': args.request_id, 'unit': args.unit, 'binding': b, 'outcome': 'entered',
               'files': freeze(root, state, u, 'entry-' + args.request_id, b)}
        data['owner'] = {'request_id': args.request_id, 'context': b['context']}
        data['entries'].append(row)
        remember(state, args.request_id, payload, row)
        save(root, state)
        return row
    except Exception:
        # Only undo an unregistered claim. If atomic persistence already made
        # the owner visible, preserve it for normal managed recovery.
        persisted = G.read_json(G.task_path(root, state['task_id']))
        if persisted['units'][args.unit]['owner'] is None:
            release_writer(root, state, u)
        raise



def acceptance(body, b):
    need(set(body) == {'outcome', 'acceptance'}, 'accepted_risk requires explicit acceptance metadata')
    a = body['acceptance']
    need(isinstance(a, dict) and set(a) == {'human', 'source', 'artifact', 'reason'}, 'invalid acceptance metadata')
    for key in a:
        text(a[key], 'acceptance ' + key)
    need(a['artifact'] == b['artifact'], 'acceptance artifact is stale')
    return a


def complete(root, state, args, body):
    payload = {'command': 'complete-unit', 'unit': args.unit, 'body': body}
    previous = remember(state, args.request_id, payload)
    if previous:
        cleanup_released_writer(root, state, definition(state, args.unit))
        return previous
    u, data = active(root, state, args.unit)
    b = binding(root, state, u)
    outcome = body.get('outcome', 'passed')
    need(outcome in ('passed', 'accepted_risk'), 'invalid completion outcome')
    accepted = acceptance(body, b) if outcome == 'accepted_risk' else None
    if outcome == 'passed':
        need(set(body) <= {'outcome'}, 'invalid completion fields')
        need(evidence(root, state, args.unit, b), 'completion evidence missing, failed, or stale')
    need(not any(r.get('outcome') == 'pending' for rs in data['checks'].values() for r in rs) and
         not any(r.get('outcome') == 'pending' for rs in data['reviews'].values() for r in rs), 'pending work must be finished or abandoned')
    row = {'receipt_id': args.request_id, 'unit': args.unit, 'outcome': outcome, 'binding': b,
           'files': freeze(root, state, u, 'complete-' + args.request_id, b)}
    if accepted:
        row['acceptance'] = accepted
    inherited = [unit(state, n)['completions'][-1] for n in u['needs'] if unit(state, n)['completions'][-1]['outcome'] == 'accepted_risk']
    if inherited:
        row['inherited_acceptances'] = [{'unit': r['unit'], 'receipt_id': r['receipt_id'], 'receipt_digest': G.digest(G.encode(r))} for r in inherited]
        row['outcome'] = 'accepted_risk'
    data['completions'].append(row)
    data['owner'] = None
    remember(state, args.request_id, payload, row)
    save_released_writer(root, state, u, was_owned=True)
    return row


def run(root, args):
    # The kernel lease is acquired before the pending receipt becomes visible.
    # It remains held through launch and finalization, and is inherited by the
    # owned command. A dead CLI therefore cannot leave an unobservable spawn gap.
    with ExitStack() as execution:
        with G.lock(root):
            state = load(root, args.task_id)
            u, data = active(root, state, args.unit)
            need(not any(rs and rs[-1]['outcome'] == 'pending' for rs in data['reviews'].values()), 'review snapshot frozen; finish or abandon review before managed checks')
            check = next((c for c in u['checks'] if c['id'] == args.check), None)
            need(check is not None, 'unknown check')
            rows = data['checks'].setdefault(args.check, [])
            need(not rows or rows[-1]['outcome'] != 'pending', 'check already pending')
            b = binding(root, state, u)
            attempt = rows[-1]['attempt'] + 1 if rows else 1
            # Archive settled receipts before replacing the inline history. A retry
            # after partial archiving must preserve, never overwrite, prior evidence.
            previous = None
            for settled in rows:
                archive = args.unit + '-check-' + args.check + '-' + str(settled['attempt']) + '.receipt.json'
                encoded = G.encode(settled)
                target = G.safe_path(directory(root, state) / archive)
                if target.exists():
                    need(G.file_digest(target) == G.digest(encoded), 'archived check receipt conflicts with current history')
                else:
                    G.atomic_write(target, encoded)
                    target.chmod(0o400)
                previous = {'path': archive, 'digest': G.digest(encoded)}
            prefix = args.unit + '-check-' + args.check + '-' + str(attempt)
            lease_path = G.safe_path(directory(root, state) / (prefix + '.lease'))
            lease = execution.enter_context(lease_path.open('a+b'))
            G.fcntl.flock(lease, G.fcntl.LOCK_EX | G.fcntl.LOCK_NB)
            invocation = {'id': G.digest(os.urandom(32)), 'owner_pid': os.getpid(),
                          'lease': prefix + '.lease', 'process': prefix + '.process.json',
                          'log': prefix + '.log', 'scope': 'process-group-and-inherited-lease'}
            row = {'attempt': attempt, 'binding': b, 'outcome': 'pending',
                   'execution': 'incomplete', 'files': {}, 'invocation': invocation}
            if previous is not None:
                row['previous_receipt'] = previous
            rows[:] = [row]
            save(root, state)
            run_cwd = cwd(root, u)
        return execute_check(root, args, state, check, run_cwd, row, lease)


def execute_check(root, args, state, check, run_cwd, row, lease):
    name = args.unit + '-check-' + args.check + '-' + str(row['attempt']) + '.log'
    path = directory(root, state) / name
    exit_code, outcome = None, 'inconclusive'
    invocation = row['invocation']
    process_path = directory(root, state) / invocation['process']
    def register_process():
        # This CLI is single-threaded. Popen has already created a new session;
        # persist its group before exec, while the inherited lease is still held.
        G.atomic_write(process_path, G.encode({'invocation_id': invocation['id'],
                                             'pid': os.getpid(), 'pgid': os.getpgrp()}))
    # Stream output with the v1 bounded runner, preserving timeout/descendant behavior.
    with path.open('xb') as output:
        process = None
        try:
            process = subprocess.Popen(check['argv'], cwd=run_cwd, env=G.workspace_env(), stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, start_new_session=True,
                                       pass_fds=(lease.fileno(),), preexec_fn=register_process)
            deadline, written = G.time.monotonic() + args.timeout, 0
            with G.selectors.DefaultSelector() as selector:
                selector.register(process.stdout, G.selectors.EVENT_READ)
                while selector.get_map():
                    remaining = deadline - G.time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(check['argv'], args.timeout)
                    for key, _ in selector.select(remaining):
                        chunk = os.read(key.fd, 65536)
                        if not chunk:
                            selector.unregister(key.fileobj)
                        else:
                            need(written + len(chunk) <= G.MAX_LOG, 'check log limit exceeded')
                            output.write(chunk)
                            output.flush()
                            written += len(chunk)
            exit_code = process.wait(timeout=max(0, deadline - G.time.monotonic()))
            outcome = 'passed' if exit_code == 0 else 'failed'
        except (subprocess.TimeoutExpired, G.GateError):
            outcome = 'inconclusive'
        except OSError:
            outcome = 'blocked'
        finally:
            if process:
                try:
                    os.killpg(process.pid, G.signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                process.stdout.close()
    with G.lock(root, wait=True):
        state = load(root, args.task_id)
        row = unit(state, args.unit)['checks'][args.check][-1]
        need(row['outcome'] == 'pending', 'check reservation no longer pending')
        # Closing our reference (not LOCK_UN) preserves a descendant's inherited
        # flock. Probe through a new open description while recovery is locked out.
        lease.close()
        try:
            with quiescent_check(root, state, row):
                pass
        except (G.GateError, OSError) as error:
            row.update(execution='incomplete', exit_code=exit_code,
                       files={name: G.file_digest(path)}, quiescence_error=str(error))
            if process_path.exists():
                row['files'][invocation['process']] = G.file_digest(process_path)
            save(root, state)
            return row
        row.update(outcome='inconclusive', execution='complete' if exit_code is not None else 'incomplete',
                   exit_code=exit_code, files={name: G.file_digest(path)})
        if process_path.exists():
            row['files'][invocation['process']] = G.file_digest(process_path)
        try:
            active(root, state, args.unit)
            if binding(root, state, definition(state, args.unit)) == row['binding']:
                row['outcome'] = outcome
        except (G.GateError, OSError):
            pass
        finally:
            save(root, state)
        return row


def zombie_group(pgid):
    """Accept only two identical, nonempty Linux zombie-only snapshots.

    A zombie cannot execute or spawn. Unknown visibility, a live member, or
    changing membership leaves the conservative killpg result in force.
    """
    if sys.platform != 'linux':
        return False
    def snapshot():
        members = {}
        try:
            for entry in Path('/proc').iterdir():
                if not entry.name.isdecimal():
                    continue
                try:
                    fields = (entry / 'stat').read_text().rsplit(') ', 1)[1].split()
                except FileNotFoundError:
                    continue  # A process that exited during enumeration.
                if int(fields[2]) == pgid:
                    # A dead thread-group leader can still have live workers.
                    # Only a single-thread zombie is proof of stopped execution.
                    if fields[0] not in ('Z', 'X') or int(fields[17]) != 1:
                        return None
                    members[entry.name] = fields[19]  # starttime guards PID reuse.
        except (OSError, ValueError, IndexError):
            return None
        return members or None
    first = snapshot()
    return first is not None and first == snapshot()


@contextmanager
def quiescent_check(root, state, row):
    """Prove that neither an inherited lease holder nor an owned group remains.

    Commands must remain in their registered process group or retain the lease
    in descendants. Deliberate daemonization that leaves the group and closes
    the lease is outside this managed execution contract, not a sandbox escape
    this helper claims to detect. PID reuse/permission uncertainty fails closed.
    """
    invocation = row.get('invocation')
    need(isinstance(invocation, dict) and invocation.get('scope') == 'process-group-and-inherited-lease',
         'pending check has no durable invocation ownership; operator verification is required')
    lease_path = G.safe_path(directory(root, state) / invocation['lease'])
    need(lease_path.is_file(), 'invocation lease evidence missing; cannot establish quiescence')
    with lease_path.open('r+b') as lease:
        try:
            G.fcntl.flock(lease, G.fcntl.LOCK_EX | G.fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise G.GateError('check invocation or an owned descendant is still active; wait for completion') from error
        process_path = directory(root, state) / invocation['process']
        process = None
        if process_path.exists():
            process = G.read_json(process_path)
            need(process.get('invocation_id') == invocation['id'] and
                 type(process.get('pid')) is int and process['pid'] > 0 and
                 process.get('pgid') == process['pid'], 'invocation process identity is invalid')
            try:
                os.killpg(process['pgid'], 0)
            except ProcessLookupError:
                pass
            except PermissionError as error:
                raise G.GateError('owned process group liveness is unknown; cannot recover') from error
            else:
                need(zombie_group(process['pgid']), 'owned process group is still active; wait for completion')
        yield process


def recover_pending_checks(root, state, data):
    """Recover only quiescent invocations owned by this task; never signal them."""
    for rows in data['checks'].values():
        for row in rows:
            if row['outcome'] != 'pending':
                continue
            invocation = row.get('invocation')
            with quiescent_check(root, state, row) as process:
                # Neither a runner/lease holder nor an owned group remains. A
                # missing process record means execution never passed pre-exec.
                evidence_files = {}
                for name in (invocation['log'], invocation['process']):
                    path = directory(root, state) / name
                    if path.exists():
                        evidence_files[name] = G.file_digest(path)
                row.update(outcome='inconclusive', execution='incomplete', exit_code=None,
                           files=evidence_files,
                           recovery={'reason': 'interrupted_without_completion_receipt',
                                     'invocation_id': invocation['id'], 'owner_pid': invocation['owner_pid'],
                                     'lease': 'released', 'process_group': 'ended' if process else 'not_started'})


def review_pending(data, args):
    rows = data['reviews'][args.gate]
    need(rows and rows[-1]['attempt'] == args.attempt and rows[-1]['outcome'] == 'pending', 'review is not current pending round')
    return rows[-1]


def prepare(root, state, args, body):
    u, data = active(root, state, args.unit)
    need(u['review'] != 'checks', 'unit has checks-only policy')
    need(not any(rs and rs[-1]['outcome'] == 'pending' for rs in data['reviews'].values()), 'another review round is pending')
    b = binding(root, state, u)
    for c in u['checks']:
        rows = data['checks'][c['id']]
        need(rows and current(root, state, rows[-1], b) and rows[-1]['outcome'] == 'passed', 'checks not currently passed')
    rows = data['reviews'][args.gate]
    need(not rows or rows[-1]['outcome'] != 'pending', 'review round already pending')
    need(len(rows) < 5, 'five repair/review rounds exhausted; budget persists across resume')
    scope = body.get('scope', 'full')
    need(scope in ('full', 'focused') and set(body) <= {'scope', 'prior_round', 'impact_assessment'}, 'invalid review scope')
    normal = None
    if args.gate == 'red-team':
        need(u['review'] == 'red-team' and scope == 'full', 'red-team requires high-risk policy and full scope')
        normal_rows = data['reviews']['final-review']
        need(normal_rows and review_current(root, state, normal_rows[-1], b) and normal_rows[-1]['outcome'] == 'passed', 'normal review must currently pass')
        normal = G.digest(G.encode(normal_rows[-1]))
    prior = None
    if scope == 'focused':
        prior = body.get('prior_round')
        need(type(prior) is int and 0 < prior <= len(rows), 'explicit prior full round required')
        p = rows[prior - 1]
        need(p['scope'] == 'full' and p['outcome'] in ('passed', 'failed') and 'adjudication' in p and p['binding']['context'] == b['context'] and
             valid_files(root, state, p), 'prior full evidence is not valid for reuse')
        text(body.get('impact_assessment'), 'impact assessment')
    source = G.safe_path(Path(args.package).absolute())
    need(source.is_file(), 'required file is unavailable')
    with tempfile.TemporaryFile() as package:
        fingerprint, nonempty = G.hashlib.sha256(), False
        with source.open('rb') as stream:
            for chunk in iter(lambda: stream.read(64 * 1024), b''):
                nonempty = nonempty or bool(chunk.strip())
                fingerprint.update(chunk)
                package.write(chunk)
        need(nonempty, 'empty review package')
        package.seek(0)
        return prepare_frozen(root, state, args, body, u, data, b, rows, scope, normal, prior,
                              package, 'sha256:' + fingerprint.hexdigest())


def prepare_frozen(root, state, args, body, u, data, b, rows, scope, normal, prior, package, fingerprint):
    prefix = args.unit + '-' + args.gate + '-' + str(len(rows) + 1)
    name = prefix + '-input.md'
    role = 'red_team' if args.gate == 'red-team' else ('focused_review' if scope == 'focused' else 'general_review')
    overrides = u.get('review_profiles', {})
    host = state.get('host', 'codex')
    profile = profile_validate(overrides.get(role, profiles(host)[role]))
    requested = {'model': profile['model'], 'effort': profile['effort'], 'reviewers': profile['count']}
    profile_source = overrides['source'] if role in overrides else ('packaged claude-model-profiles.json' if host == 'claude-code' else 'packaged model-profiles.json')
    row = {'attempt': len(rows) + 1, 'unit': args.unit, 'gate': args.gate, 'scope': scope,
           'prior_round': prior, 'impact_assessment': body.get('impact_assessment'), 'normal_review': normal,
           'binding': b, 'requested': requested, 'profile_source': profile_source, 'raw': [], 'outcome': 'pending',
           'files': freeze(root, state, u, prefix[len(args.unit) + 1:] + '-snapshot', b)}
    if prior is not None:
        p = rows[prior - 1]
        chain = focused_chain(data, prior, b['context'])
        for earlier in chain:
            row['files'].update(earlier['files'])
        row['prior_review'] = {'attempt': prior, 'outcome': p['outcome'], 'adjudication': p['adjudication'], 'files': p['files']}
        row['intervening_reviews'] = [{'attempt': r['attempt'], 'outcome': r['outcome'], 'adjudication': r['adjudication'], 'files': r['files']} for r in chain if r['attempt'] > prior]
        row['unresolved_prior_findings'] = sorted(unresolved_findings(chain))
    G.atomic_chunks(directory(root, state) / name, iter(lambda: package.read(64 * 1024), b''))
    (directory(root, state) / name).chmod(0o400)
    row['files'][name] = fingerprint
    row['package'] = str(directory(root, state) / name)
    rows.append(row)
    save(root, state)
    return row


def record(root, state, args, body):
    u, data = active(root, state, args.unit)
    row = review_pending(data, args)
    b = binding(root, state, u)
    need(review_current(root, state, row, b), 'review reservation stale')
    need(len(row['raw']) < row['requested']['reviewers'], 'all reviewer slots already recorded')
    reviewer = G.identifier(args.reviewer_id)
    need(reviewer not in state['sessions'], 'reviewer cannot be controller')
    fields = {'run_id', 'execution', 'verdict', 'findings', 'observed'}
    if args.gate == 'red-team':
        fields.add('challenge_verdict')
    need(set(body) == fields, 'invalid raw review fields')
    if args.gate == 'red-team':
        need(body['challenge_verdict'] in ('survives_challenge', 'invalidated', 'inconclusive', 'blocked'), 'invalid challenge verdict')
    run_id = G.identifier(body['run_id'])
    all_raw = [r for d in state['units'].values() for rs in d['reviews'].values() for review in rs for r in review['raw']]
    need(all(r['run_id'] != run_id and r['reviewer_id'] != reviewer for r in all_raw), 'reviewers require distinct fresh runs and identities')
    need(body['execution'] in ('complete', 'incomplete') and body['verdict'] in ('passed', 'failed', 'inconclusive', 'blocked'), 'invalid raw verdict')
    observed = body['observed']
    need(isinstance(observed, dict) and set(observed) == {'model', 'effort'}, 'record observed model/effort or unknown')
    for name in ('model', 'effort'):
        text(observed[name], 'observed ' + name)
    findings = body['findings']
    need(isinstance(findings, list), 'invalid findings')
    ids = []
    for finding in findings:
        need(isinstance(finding, dict) and set(finding) == {'id', 'title', 'location', 'evidence', 'impact'}, 'invalid finding fields')
        ids.append(G.identifier(finding['id']))
        for key in ('title', 'location', 'evidence', 'impact'):
            text(finding[key], key)
    need(len(ids) == len(set(ids)), 'duplicate finding ID')
    if args.gate == 'red-team' and body['challenge_verdict'] == 'invalidated':
        need(findings, 'invalidated challenge requires counterexample findings')
    report = G.read_file(Path(args.report).absolute(), G.MAX_REPORT)
    need(report.strip(), 'empty reviewer report')
    name = args.unit + '-' + args.gate + '-' + str(args.attempt) + '-' + reviewer + '.md'
    G.atomic_write(directory(root, state) / name, report)
    (directory(root, state) / name).chmod(0o400)
    row['files'][name] = G.digest(report)
    raw = dict(body, reviewer_id=reviewer, report=name, report_digest=G.digest(report), requested=row['requested'])
    row['raw'].append(raw)
    save(root, state)
    return raw


def adjudicate(root, state, args, body):
    u, data = active(root, state, args.unit)
    row = review_pending(data, args)
    need(review_current(root, state, row, binding(root, state, u)), 'review reservation stale')
    need(len(row['raw']) == row['requested']['reviewers'], 'missing reviewer evidence')
    need(all(r['execution'] == 'complete' and r['verdict'] in ('passed', 'failed') for r in row['raw']), 'incomplete or inconclusive reviewer blocks adjudication')
    need(all(r['observed'][k] in ('unknown', row['requested'][k]) or (k == 'effort' and row['requested'][k] == 'inherit')
             for r in row['raw'] for k in ('model', 'effort')), 'observed reviewer configuration mismatches request')
    if args.gate == 'red-team':
        need(all(r['challenge_verdict'] in ('survives_challenge', 'invalidated') for r in row['raw']), 'inconclusive or blocked challenge prevents adjudication')
    findings = {r['reviewer_id'] + ':' + f['id']: f for r in row['raw'] for f in r['findings']}
    need(all(r['verdict'] != 'failed' or r['findings'] for r in row['raw']), 'failed verdict lacks finding evidence')
    need(isinstance(body, dict) and {'decisions'} <= set(body) <= {'decisions', 'resolutions'} and isinstance(body['decisions'], list), 'invalid adjudication fields')
    resolutions = body.get('resolutions', [])
    need(isinstance(resolutions, list), 'invalid resolution evidence')
    expected_resolutions = set()
    if row['scope'] == 'focused':
        chain = focused_chain(data, row['prior_round'], row['binding']['context'], row['attempt'])
        expected_resolutions = unresolved_findings(chain)
    seen_resolutions = set()
    for resolution in resolutions:
        need(isinstance(resolution, dict) and set(resolution) == {'finding', 'reason', 'evidence'}, 'invalid prior finding resolution')
        key = resolution['finding']
        need(key in expected_resolutions and key not in seen_resolutions, 'unknown or duplicate prior finding resolution')
        text(resolution['reason'], 'resolution reason')
        text(resolution['evidence'], 'current artifact resolution evidence')
        seen_resolutions.add(key)
    need(seen_resolutions == expected_resolutions, 'every prior blocking finding requires current artifact resolution evidence')
    decisions = {}
    for d in body['decisions']:
        need(isinstance(d, dict) and set(d) <= {'finding', 'decision', 'reason', 'evidence', 'duplicate_of', 'blocking'} and
             {'finding', 'decision', 'reason', 'evidence'} <= set(d), 'invalid finding decision')
        key = d['finding']
        need(key in findings and key not in decisions, 'unknown or duplicate finding decision')
        need(d['decision'] in ('valid', 'dismissed', 'duplicate'), 'invalid adjudication decision')
        if d['decision'] == 'valid':
            need(type(d.get('blocking')) is bool, 'valid finding requires explicit blocking boolean')
        else:
            need('blocking' not in d, 'blocking applies only to valid findings')
        text(d['reason'], 'decision reason')
        text(d['evidence'], 'validation evidence')
        decisions[key] = d
    need(set(decisions) == set(findings), 'each finding requires separate controller adjudication')
    for key, d in decisions.items():
        if d['decision'] == 'duplicate':
            target = d.get('duplicate_of')
            need(target in decisions and target != key and decisions[target]['decision'] != 'duplicate', 'duplicate must reference a distinct adjudicated primary finding')
        else:
            need('duplicate_of' not in d, 'duplicate_of only allowed for duplicates')
    row['adjudication'] = body
    row['outcome'] = 'failed' if any(d['decision'] == 'valid' and d['blocking'] for d in decisions.values()) else 'passed'
    if args.gate == 'red-team':
        row['challenge_verdict'] = 'invalidated' if row['outcome'] == 'failed' else 'survives_challenge'
    save(root, state)
    return {'attempt': row['attempt'], 'outcome': row['outcome'], 'adjudication': body,
            **({'challenge_verdict': row['challenge_verdict']} if args.gate == 'red-team' else {})}


def dispatch(g, root, args, config=None):
    global G
    G = g
    if args.command == 'init':
        return initialize(root, args, config)
    if args.command == 'run':
        need(0 < args.timeout <= 3600, 'timeout must be between 0 and 3600 seconds')
        return run(root, args)
    body = read_input() if args.command in ('enter', 'complete-unit', 'prepare-review', 'record-review', 'adjudicate') else {}
    with G.lock(root):
        state = load(root, args.task_id)
        if args.command in ('status', 'check', 'ready'):
            return inspect(root, state)
        if args.command == 'enter':
            return enter(root, state, args, body)
        if args.command == 'complete-unit':
            return complete(root, state, args, body)
        if args.command == 'prepare-review':
            return prepare(root, state, args, body)
        if args.command == 'record-review':
            return record(root, state, args, body)
        if args.command == 'adjudicate':
            return adjudicate(root, state, args, body)
        if args.command == 'revise':
            validate(config, root)
            need(not state['closed'], 'task is closed')
            need({u['id'] for u in config['units']} == set(state['units']), 'revise preserves IDs and budgets')
            need(all(d['owner'] is None for d in state['units'].values()), 'abandon managed writers before revise')
            if config != state['config']:
                validate_revision(state, config)
                state['config_history'].append(state['config'])
                state['config'] = config
                for u in config['units']:
                    for c in u['checks']:
                        unit(state, u['id'])['checks'].setdefault(c['id'], [])
        elif args.command == 'abandon':
            data = unit(state, args.unit)
            was_owned = data['owner'] is not None
            # A live invocation remains protected; interrupted invocations can
            # be abandoned only after their durable ownership proves quiescent.
            recover_pending_checks(root, state, data)
            for rs in data['reviews'].values():
                if rs and rs[-1]['outcome'] == 'pending':
                    rs[-1]['outcome'] = 'inconclusive'
            data['owner'] = None
            save_released_writer(root, state, definition(state, args.unit), was_owned)
            return inspect(root, state)
        elif args.command == 'close':
            status = inspect(root, state)
            if args.outcome == 'accepted_risk':
                need(status['complete'] and any(u['status'] == 'accepted_risk' for u in status['units'].values()),
                     'accepted_risk closure requires a current accepted_risk unit and all units complete')
            else:
                need(args.outcome == 'superseded' or status['ready'], 'all units must currently pass or explicitly close accepted risk')
            need(all(d['owner'] is None for d in state['units'].values()), 'abandon active units before close')
            for u in state['config']['units']:
                cleanup_released_writer(root, state, u)
            state['closed'] = args.outcome
        else:
            raise G.GateError('unsupported managed command')
        save(root, state)
        return inspect(root, state)
