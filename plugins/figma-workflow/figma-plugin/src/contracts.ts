export type ReasonCode =
  | 'INVALID_JSON'
  | 'UNSUPPORTED_VERSION'
  | 'UNKNOWN_OPERATION'
  | 'UNKNOWN_FIELD'
  | 'INVALID_FIELD'
  | 'DUPLICATE_TARGET'
  | 'PREVIEW_REQUIRED'
  | 'PLAN_CHANGED'
  | 'PREVIEW_NOT_READY'
  | 'READY'
  | 'MISSING_NODE'
  | 'WRONG_NODE_TYPE'
  | 'STALE_EXPECTED_STATE'
  | 'ALREADY_DESIRED'
  | 'LOOKUP_FAILED'
  | 'IMPORT_FAILED'
  | 'MUTATION_FAILED'
  | 'READBACK_FAILED'
  | 'READBACK_MISMATCH'
  | 'AUTO_LAYOUT_FILL_WITHOUT_AUTO_PARENT'
  | 'AUTO_LAYOUT_ABSOLUTE_WITHOUT_AUTO_PARENT'
  | 'PROTOTYPE_EMPTY_ACTIONS'
  | 'PROTOTYPE_DESTINATION_MISSING';

export type PlanValidation = { status: 'invalid'; reason: ReasonCode };

export type ReadOnlyOperation =
  | 'inspect-selection'
  | 'audit-auto-layout'
  | 'audit-prototype-links';

export type ReadOnlyPlan = {
  version: 1;
  mode: 'preview';
  operation: ReadOnlyOperation;
  scope: { kind: 'selection' };
};

export type RenameTarget = {
  nodeId: string;
  expectedName: string;
  newName: string;
};

export type RenamePlan = {
  version: 1;
  mode: 'preview' | 'apply';
  operation: 'rename-exact';
  targets: RenameTarget[];
};

export type IconSwapTarget = {
  nodeId: string;
  expectedMainComponentKey: string;
  replacementComponentKey: string;
};

export type IconSwapPlan = {
  version: 1;
  mode: 'preview' | 'apply';
  operation: 'replace-icon-instance-exact';
  targets: IconSwapTarget[];
};

export type OperationPlan = ReadOnlyPlan | RenamePlan | IconSwapPlan;
export type ParseResult = OperationPlan | PlanValidation;

export type NormalizedNodeSnapshot = {
  id: string;
  type: string;
  name: string;
  mainComponentKey?: string;
  layoutMode?: string;
  layoutSizingHorizontal?: string;
  layoutSizingVertical?: string;
  layoutPositioning?: string;
  parent?: Pick<NormalizedNodeSnapshot, 'id' | 'type' | 'layoutMode'>;
  reactions?: Array<{ actions?: Array<{ destinationId?: string }> }>;
  children?: NormalizedNodeSnapshot[];
};

export type PreviewReceipt = {
  fingerprint: string;
  targets: Array<{
    nodeId: string;
    disposition: ReasonCode;
    expectedName?: string;
    expectedMainComponentKey?: string;
    observedName?: string;
    observedMainComponentKey?: string;
  }>;
};

export type TargetResult = {
  nodeId: string;
  status: 'ready' | 'skipped' | 'applied' | 'failed';
  reason: ReasonCode;
  before?: Record<string, string | undefined>;
  after?: Record<string, string | undefined>;
  observed?: Record<string, string | undefined>;
};

export type PreviewResult = {
  status: 'failed' | 'ready' | 'partial' | 'no_changes';
  results: TargetResult[];
  receipt: PreviewReceipt;
};

export type ApplyResult = {
  status: 'failed' | 'partial' | 'applied' | 'no_changes';
  results: TargetResult[];
};

export type AuditFinding = {
  code:
    | 'AUTO_LAYOUT_FILL_WITHOUT_AUTO_PARENT'
    | 'AUTO_LAYOUT_ABSOLUTE_WITHOUT_AUTO_PARENT'
    | 'PROTOTYPE_EMPTY_ACTIONS'
    | 'PROTOTYPE_DESTINATION_MISSING';
  nodeId: string;
  observed: Record<string, string | undefined>;
};

export type InspectionResult = {
  status: 'inspected';
  nodes: NormalizedNodeSnapshot[];
};

export type AuditResult = {
  status: 'findings' | 'clean';
  findings: AuditFinding[];
};
