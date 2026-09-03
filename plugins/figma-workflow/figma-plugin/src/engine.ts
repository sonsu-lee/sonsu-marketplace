import type {
  IconSwapPlan,
  IconSwapTarget,
  OperationPlan,
  ParseResult,
  ApplyResult,
  AuditFinding,
  AuditResult,
  InspectionResult,
  PlanValidation,
  PreviewReceipt,
  PreviewResult,
  ReadOnlyPlan,
  RenamePlan,
  RenameTarget,
  TargetResult,
} from './contracts.js';
import type { NodePort } from './ports.js';

const invalid = (reason: PlanValidation['reason']): PlanValidation => ({ status: 'invalid', reason });

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const hasOnlyFields = (value: Record<string, unknown>, fields: readonly string[]): boolean =>
  Object.keys(value).every((key) => fields.includes(key));

const isNonBlankString = (value: unknown): value is string =>
  typeof value === 'string' && value.trim().length > 0;

function parseReadOnlyPlan(value: Record<string, unknown>): ReadOnlyPlan | PlanValidation {
  if (!hasOnlyFields(value, ['version', 'mode', 'operation', 'scope'])) return invalid('UNKNOWN_FIELD');
  if (value.mode !== 'preview' || !isRecord(value.scope)) return invalid('INVALID_FIELD');
  if (!hasOnlyFields(value.scope, ['kind']) || value.scope.kind !== 'selection') return invalid('UNKNOWN_FIELD');

  return value as ReadOnlyPlan;
}

function parseRenameTarget(value: unknown): RenameTarget | PlanValidation {
  if (!isRecord(value)) return invalid('INVALID_FIELD');
  if (!hasOnlyFields(value, ['nodeId', 'expectedName', 'newName'])) return invalid('UNKNOWN_FIELD');
  if (!isNonBlankString(value.nodeId) || !isNonBlankString(value.expectedName) || !isNonBlankString(value.newName)) {
    return invalid('INVALID_FIELD');
  }
  if (value.expectedName === value.newName) return invalid('INVALID_FIELD');
  return value as RenameTarget;
}

function parseIconSwapTarget(value: unknown): IconSwapTarget | PlanValidation {
  if (!isRecord(value)) return invalid('INVALID_FIELD');
  if (!hasOnlyFields(value, ['nodeId', 'expectedMainComponentKey', 'replacementComponentKey'])) {
    return invalid('UNKNOWN_FIELD');
  }
  if (!isNonBlankString(value.nodeId) || !isNonBlankString(value.expectedMainComponentKey) || !isNonBlankString(value.replacementComponentKey)) {
    return invalid('INVALID_FIELD');
  }
  if (value.expectedMainComponentKey === value.replacementComponentKey) return invalid('INVALID_FIELD');
  return value as IconSwapTarget;
}

function parseMutationPlan<T extends RenameTarget | IconSwapTarget>(
  value: Record<string, unknown>,
  operation: 'rename-exact' | 'replace-icon-instance-exact',
  parseTarget: (target: unknown) => T | PlanValidation,
): (RenamePlan | IconSwapPlan) | PlanValidation {
  if (!hasOnlyFields(value, ['version', 'mode', 'operation', 'targets'])) return invalid('UNKNOWN_FIELD');
  if (value.mode !== 'preview' && value.mode !== 'apply') return invalid('INVALID_FIELD');
  if (!Array.isArray(value.targets) || value.targets.length === 0) return invalid('INVALID_FIELD');

  const targets: T[] = [];
  const nodeIds = new Set<string>();
  for (const rawTarget of value.targets) {
    const target = parseTarget(rawTarget);
    if ('status' in target) return target;
    if (nodeIds.has(target.nodeId)) return invalid('DUPLICATE_TARGET');
    nodeIds.add(target.nodeId);
    targets.push(target);
  }

  return { version: 1, mode: value.mode, operation, targets } as RenamePlan | IconSwapPlan;
}

export function parsePlan(text: string): ParseResult {
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch {
    return invalid('INVALID_JSON');
  }

  if (!isRecord(value)) return invalid('INVALID_FIELD');
  if (!hasOnlyFields(value, ['version', 'mode', 'operation', 'scope', 'targets'])) return invalid('UNKNOWN_FIELD');
  if (value.version !== 1) return invalid('UNSUPPORTED_VERSION');

  switch (value.operation) {
    case 'inspect-selection':
    case 'audit-auto-layout':
    case 'audit-prototype-links':
      return parseReadOnlyPlan(value);
    case 'rename-exact':
      return parseMutationPlan(value, 'rename-exact', parseRenameTarget);
    case 'replace-icon-instance-exact':
      return parseMutationPlan(value, 'replace-icon-instance-exact', parseIconSwapTarget);
    default:
      return invalid('UNKNOWN_OPERATION');
  }
}

const isMutationPlan = (plan: OperationPlan): plan is RenamePlan | IconSwapPlan =>
  plan.operation === 'rename-exact' || plan.operation === 'replace-icon-instance-exact';

const canonicalFingerprint = (plan: RenamePlan | IconSwapPlan): string => {
  if (plan.operation === 'rename-exact') {
    return JSON.stringify({ operation: plan.operation, targets: plan.targets.map((target) => {
      return {
        expectedName: target.expectedName,
        newName: target.newName,
        nodeId: target.nodeId,
      };
    }) });
  }
  return JSON.stringify({ operation: plan.operation, targets: plan.targets.map((target) => ({
      expectedMainComponentKey: target.expectedMainComponentKey,
      nodeId: target.nodeId,
      replacementComponentKey: target.replacementComponentKey,
    })) });
};

function aggregatePreview(results: TargetResult[]): PreviewResult['status'] {
  if (results.every((result) => result.status === 'skipped')) return 'no_changes';
  return results.some((result) => result.status === 'skipped') ? 'partial' : 'ready';
}

function aggregateApply(results: TargetResult[]): ApplyResult['status'] {
  const applied = results.some((result) => result.status === 'applied');
  const failed = results.some((result) => result.status === 'failed');
  const skipped = results.some((result) => result.status === 'skipped');
  if (failed && !applied) return 'failed';
  if (applied && (failed || skipped)) return 'partial';
  if (applied) return 'applied';
  return 'no_changes';
}

function hasMatchingReceipt(receipt: unknown, plan: RenamePlan | IconSwapPlan): receipt is PreviewReceipt {
  if (!isRecord(receipt) || receipt.fingerprint !== canonicalFingerprint(plan) || !Array.isArray(receipt.targets)) return false;
  if (receipt.targets.length !== plan.targets.length) return false;
  return receipt.targets.every((candidate, index) => {
    if (!isRecord(candidate) || candidate.nodeId !== plan.targets[index].nodeId) return false;
    if (plan.operation === 'rename-exact') {
      return candidate.expectedName === plan.targets[index].expectedName;
    }
    return candidate.expectedMainComponentKey === plan.targets[index].expectedMainComponentKey;
  });
}

const isAutoLayout = (layoutMode: string | undefined): boolean =>
  layoutMode === 'HORIZONTAL' || layoutMode === 'VERTICAL';

const observedFields = (fields: Record<string, string | undefined>): Record<string, string> => {
  const observed: Record<string, string> = {};
  for (const [key, value] of Object.entries(fields)) {
    if (value !== undefined) observed[key] = value;
  }
  return observed;
};

async function inspectOrAudit(plan: ReadOnlyPlan, port: NodePort): Promise<PlanValidation | InspectionResult | AuditResult> {
  const roots = await port.getSelection();
  if (roots.length === 0) return invalid('INVALID_FIELD');
  const nodes = JSON.parse(JSON.stringify(roots)) as typeof roots;
  if (plan.operation === 'inspect-selection') return { status: 'inspected', nodes };

  const flattened: Array<{ node: typeof nodes[number]; parent: typeof nodes[number]['parent'] }> = [];
  const visit = (node: typeof nodes[number], parent?: typeof nodes[number]) => {
    const effectiveParent = node.parent ?? (parent && { id: parent.id, type: parent.type, layoutMode: parent.layoutMode });
    flattened.push({ node, parent: effectiveParent });
    for (const child of node.children ?? []) visit(child, node);
  };
  for (const root of nodes) visit(root);

  const findings: AuditFinding[] = [];
  if (plan.operation === 'audit-auto-layout') {
    for (const { node, parent } of flattened) {
      if ((node.layoutSizingHorizontal === 'FILL' || node.layoutSizingVertical === 'FILL') && !isAutoLayout(parent?.layoutMode)) {
        findings.push({
          code: 'AUTO_LAYOUT_FILL_WITHOUT_AUTO_PARENT',
          nodeId: node.id,
          observed: observedFields({
            layoutSizingHorizontal: node.layoutSizingHorizontal,
            layoutSizingVertical: node.layoutSizingVertical,
            parentLayoutMode: parent?.layoutMode,
          }),
        });
      }
      if (node.layoutPositioning === 'ABSOLUTE' && !isAutoLayout(parent?.layoutMode)) {
        findings.push({
          code: 'AUTO_LAYOUT_ABSOLUTE_WITHOUT_AUTO_PARENT',
          nodeId: node.id,
          observed: observedFields({ layoutPositioning: node.layoutPositioning, parentLayoutMode: parent?.layoutMode }),
        });
      }
    }
  } else {
    for (const { node } of flattened) {
      for (const [reactionIndex, reaction] of (node.reactions ?? []).entries()) {
        if (!reaction.actions || reaction.actions.length === 0) {
          findings.push({ code: 'PROTOTYPE_EMPTY_ACTIONS', nodeId: node.id, observed: { reactionIndex: String(reactionIndex) } });
          continue;
        }
        for (const action of reaction.actions) {
          if (!action.destinationId) continue;
          if (await port.readNode(action.destinationId) === null) {
            findings.push({ code: 'PROTOTYPE_DESTINATION_MISSING', nodeId: node.id, observed: { destinationId: action.destinationId } });
          }
        }
      }
    }
  }
  return { status: findings.length > 0 ? 'findings' : 'clean', findings };
}

export async function previewPlan(text: string, port: NodePort): Promise<PlanValidation | PreviewResult | InspectionResult | AuditResult> {
  const parsed = parsePlan(text);
  if ('status' in parsed) return parsed;
  if (!isMutationPlan(parsed)) return inspectOrAudit(parsed, port);

  const results: TargetResult[] = [];
  const receiptTargets: PreviewReceipt['targets'] = [];
  for (const target of parsed.targets) {
    const node = await port.readNode(target.nodeId);
    if (parsed.operation === 'rename-exact') {
      const renameTarget = target as RenameTarget;
      receiptTargets.push({ nodeId: target.nodeId, expectedName: renameTarget.expectedName, observedName: node?.name });
      if (node === null) {
        results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'MISSING_NODE' });
      } else if (node.name === renameTarget.newName) {
        results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'ALREADY_DESIRED' });
      } else if (node.name !== renameTarget.expectedName) {
        results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'STALE_EXPECTED_STATE' });
      } else {
        results.push({
          nodeId: target.nodeId,
          status: 'ready',
          reason: 'READY',
          before: { name: node.name },
          after: { name: renameTarget.newName },
        });
      }
      continue;
    }

    const iconTarget = target as IconSwapTarget;
    receiptTargets.push({
      nodeId: target.nodeId,
      expectedMainComponentKey: iconTarget.expectedMainComponentKey,
      observedMainComponentKey: node?.mainComponentKey,
    });
    if (node === null) {
      results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'MISSING_NODE' });
    } else if (node.type !== 'INSTANCE') {
      results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'WRONG_NODE_TYPE' });
    } else if (node.mainComponentKey === iconTarget.replacementComponentKey) {
      results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'ALREADY_DESIRED' });
    } else if (node.mainComponentKey !== iconTarget.expectedMainComponentKey) {
      results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'STALE_EXPECTED_STATE' });
    } else {
      results.push({
        nodeId: target.nodeId,
        status: 'ready',
        reason: 'READY',
        before: { mainComponentKey: node.mainComponentKey },
        after: { mainComponentKey: iconTarget.replacementComponentKey },
      });
    }
  }

  return {
    status: aggregatePreview(results),
    results,
    receipt: { fingerprint: canonicalFingerprint(parsed), targets: receiptTargets },
  };
}

export async function applyPlan(text: string, receipt: unknown, port: NodePort): Promise<PlanValidation | ApplyResult> {
  const parsed = parsePlan(text);
  if ('status' in parsed) return parsed;
  if (!isMutationPlan(parsed) || parsed.mode !== 'apply') return invalid('INVALID_FIELD');
  if (receipt === undefined || receipt === null) return invalid('PREVIEW_REQUIRED');
  if (!hasMatchingReceipt(receipt, parsed)) return invalid('PLAN_CHANGED');

  const results: TargetResult[] = [];
  for (const target of parsed.targets) {
    let node;
    try {
      node = await port.readNode(target.nodeId);
    } catch {
      results.push({ nodeId: target.nodeId, status: 'failed', reason: 'LOOKUP_FAILED' });
      continue;
    }
    if (node === null) {
      results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'MISSING_NODE' });
      continue;
    }

    if (parsed.operation === 'rename-exact') {
      const renameTarget = target as RenameTarget;
      const beforeName = node.name;
      if (node.name === renameTarget.newName) {
        results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'ALREADY_DESIRED' });
        continue;
      }
      if (node.name !== renameTarget.expectedName) {
        results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'STALE_EXPECTED_STATE' });
        continue;
      }
      try {
        await port.rename(target.nodeId, renameTarget.newName);
      } catch {
        results.push({ nodeId: target.nodeId, status: 'failed', reason: 'MUTATION_FAILED' });
        continue;
      }
      try {
        const readback = await port.readNode(target.nodeId);
        if (readback?.name === renameTarget.newName) {
          results.push({
            nodeId: target.nodeId, status: 'applied', reason: 'READY',
            before: { name: beforeName }, after: { name: renameTarget.newName },
          });
        } else {
          results.push({ nodeId: target.nodeId, status: 'failed', reason: 'READBACK_MISMATCH', observed: observedFields({ name: readback?.name }) });
        }
      } catch {
        results.push({ nodeId: target.nodeId, status: 'failed', reason: 'READBACK_FAILED' });
      }
      continue;
    }

    const iconTarget = target as IconSwapTarget;
    const beforeMainComponentKey = node.mainComponentKey;
    if (node.type !== 'INSTANCE') {
      results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'WRONG_NODE_TYPE' });
      continue;
    }
    if (node.mainComponentKey === iconTarget.replacementComponentKey) {
      results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'ALREADY_DESIRED' });
      continue;
    }
    if (node.mainComponentKey !== iconTarget.expectedMainComponentKey) {
      results.push({ nodeId: target.nodeId, status: 'skipped', reason: 'STALE_EXPECTED_STATE' });
      continue;
    }
    let component: unknown;
    try {
      component = await port.importComponent(iconTarget.replacementComponentKey);
    } catch {
      results.push({ nodeId: target.nodeId, status: 'failed', reason: 'IMPORT_FAILED' });
      continue;
    }
    try {
      await port.replaceIconInstance(target.nodeId, component);
    } catch {
      results.push({ nodeId: target.nodeId, status: 'failed', reason: 'MUTATION_FAILED' });
      continue;
    }
    try {
      const readback = await port.readNode(target.nodeId);
      if (readback?.mainComponentKey === iconTarget.replacementComponentKey) {
        results.push({
          nodeId: target.nodeId, status: 'applied', reason: 'READY',
          before: { mainComponentKey: beforeMainComponentKey },
          after: { mainComponentKey: iconTarget.replacementComponentKey },
        });
      } else {
        results.push({ nodeId: target.nodeId, status: 'failed', reason: 'READBACK_MISMATCH', observed: observedFields({ mainComponentKey: readback?.mainComponentKey }) });
      }
    } catch {
      results.push({ nodeId: target.nodeId, status: 'failed', reason: 'READBACK_FAILED' });
    }
  }
  return { status: aggregateApply(results), results };
}
