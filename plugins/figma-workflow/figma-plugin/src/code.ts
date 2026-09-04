import { applyPlan, previewPlan } from './engine.js';
import { FigmaNodePort } from './figma-adapter.js';

type UiMessage = { type?: unknown; plan?: unknown; receipt?: unknown };

const port = new FigmaNodePort();

figma.showUI(__html__, { width: 520, height: 680, themeColors: true });

figma.ui.onmessage = async (message: UiMessage) => {
  if (typeof message.plan !== 'string') return;

  if (message.type === 'preview') {
    const result = await previewPlan(message.plan, port);
    figma.ui.postMessage({ type: 'result', request: 'preview', result });
    return;
  }

  if (message.type === 'apply') {
    const result = await applyPlan(message.plan, message.receipt, port);
    figma.ui.postMessage({ type: 'result', request: 'apply', result });
  }
};
