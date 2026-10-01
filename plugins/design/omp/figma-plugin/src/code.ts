import { applyPlan, previewPlan } from './engine.js';
import { FigmaNodePort } from './figma-adapter.js';
import type { NodePort } from './ports.js';

type UiRequest = { type?: unknown; plan?: unknown; input?: unknown; receipt?: unknown; requestId?: unknown };
type UiResultMessage = {
  type: 'result';
  request: 'preview' | 'apply' | 'invalid';
  requestId: number | null;
  input: string | null;
  result: unknown;
};

const invalidField = { status: 'invalid', reason: 'INVALID_FIELD' } as const;
const lookupFailed = { status: 'failed', reason: 'LOOKUP_FAILED' } as const;

const isRequestId = (value: unknown): value is number =>
  typeof value === 'number' && Number.isSafeInteger(value) && value >= 0;

const isRequest = (value: unknown): value is UiRequest =>
  typeof value === 'object' && value !== null;

export function createUiMessageHandler(
  port: NodePort,
  post: (message: UiResultMessage) => void,
): (message: unknown) => Promise<void> {
  return async (message: unknown) => {
    let request: UiResultMessage['request'] = 'invalid';
    let requestId: number | null = null;
    let input: string | null = null;
    let result: unknown = invalidField;

    try {
      if (isRequest(message) && (message.type === 'preview' || message.type === 'apply')) {
        request = message.type;
        if (typeof message.plan === 'string' && typeof message.input === 'string' && isRequestId(message.requestId)) {
          requestId = message.requestId;
          input = message.input;
          result = request === 'preview'
            ? await previewPlan(message.plan, port)
            : await applyPlan(message.plan, message.receipt, port);
        }
      }
    } catch {
      result = request === 'invalid' ? invalidField : lookupFailed;
    }

    post({ type: 'result', request, requestId, input, result });
  };
}

export function startPlugin(): void {
  const port = new FigmaNodePort();
  figma.showUI(__html__, { width: 520, height: 680, themeColors: true });
  figma.ui.onmessage = createUiMessageHandler(port, (message) => figma.ui.postMessage(message));
}

if (typeof figma !== 'undefined' && typeof __html__ !== 'undefined') startPlugin();
