import { expect, test } from 'bun:test';
import { createHarness } from './sdk-host.ts';
import type { DesignPlan } from '../src/engine.ts';
import { parseVerdict } from '../src/report.ts';

function advisory(): DesignPlan {
  return {
    mode: 'advisory', paths: [], goal: 'Advise on a single-color engraving handoff',
    brief: 'Our brand owner approved the full-color identity. The supplier needs a single-color version. What should we prepare?',
    facts: [
      { subject: 'Full-color identity', approval: 'approved', availability: 'exists-not-supplied' },
      { subject: 'Single-color variant', approval: 'not-supplied', availability: 'unknown' },
    ],
    captures: [], checks: [],
  };
}

test('an advisory report is checked against confirmed facts and published unchanged as advice', async () => {
  const prompts: string[] = [];
  const h = await createHarness([], {
    author: () => async prompt => { prompts.push(prompt); return 'Build the single-color lockup from a copy of the master. Ask the brand owner whether it needs approval.'; },
    reviewer: () => async prompt => { prompts.push(prompt); return 'Verdict: {"decision": "pass", "findings": []}'; },
  });
  try {
    h.choice.approve = true;
    await h.start(advisory());
    expect((await h.status()).missing).toEqual(['report', 'review']);
    await h.command('design-report');
    const state = await h.status();
    expect(state.missing).toEqual(['review']);
    // 検査者には作者の会話ではなく、依頼・確定事実・本文だけを渡す。
    expect(prompts[1]).toContain('| Full-color identity | approved | exists, not supplied for inspection |');
    expect(prompts[1]).toContain('| Single-color variant | not supplied (unknown) | unknown |');
    expect(prompts[1]).toContain('Ask the brand owner whether it needs approval.');
    await h.command('design-accept');
    const advised = await h.status();
    expect(advised.phase).toBe('advised');
    const published = h.published().at(-1)!;
    expect(published).toContain('No captures or checks were run. Nothing in this report was rendered or tested.');
    expect(published).toContain('Ask the brand owner whether it needs approval.');
    expect(h.errors).toEqual([]);
  } finally { await h.close(); }
});

test('a rejected or unreadable review records nothing and blocks acceptance', async () => {
  let verdict = '{"decision": "reject", "findings": [{"quote": "Approval of the new version still needs to come.", "subject": "Single-color variant", "reason": "Approval status was not supplied."}]}';
  const h = await createHarness([], {
    author: () => async () => 'Approval of the new version still needs to come.',
    reviewer: () => async () => verdict,
  });
  try {
    h.choice.approve = true;
    await h.start(advisory());
    await h.command('design-report');
    expect(h.notifications.at(-1)).toContain('"Approval of the new version still needs to come." (Single-color variant)');
    expect((await h.status()).missing).toEqual(['report', 'review']);
    verdict = 'I think it is fine.';
    await h.command('design-report');
    expect(h.notifications.at(-1)).toContain('no JSON verdict');
    await h.command('design-accept');
    expect(h.notifications.at(-1)).toContain('missing or stale: report, review');
    expect(h.published().some(text => text.startsWith('# Design report'))).toBe(false);
    expect((await h.status()).phase).toBe('active');
  } finally { await h.close(); }
});

test('a pass verdict that still lists findings is treated as a rejection', () => {
  expect(parseVerdict('{"decision": "pass", "findings": [{"quote": "q", "subject": "s", "reason": "r"}]}').decision).toBe('reject');
  expect(() => parseVerdict('{"decision": "maybe", "findings": []}')).toThrow('pass/reject');
});
