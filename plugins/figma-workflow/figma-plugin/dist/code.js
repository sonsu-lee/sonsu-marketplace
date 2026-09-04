"use strict";
(() => {
  // src/engine.ts
  var invalid = (reason) => ({ status: "invalid", reason });
  var isRecord = (value) => typeof value === "object" && value !== null && !Array.isArray(value);
  var hasOnlyFields = (value, fields) => Object.keys(value).every((key) => fields.includes(key));
  var isNonBlankString = (value) => typeof value === "string" && value.trim().length > 0;
  function parseReadOnlyPlan(value) {
    if (!hasOnlyFields(value, ["version", "mode", "operation", "scope"])) return invalid("UNKNOWN_FIELD");
    if (value.mode !== "preview" || !isRecord(value.scope)) return invalid("INVALID_FIELD");
    if (!hasOnlyFields(value.scope, ["kind"]) || value.scope.kind !== "selection") return invalid("UNKNOWN_FIELD");
    return value;
  }
  function parseRenameTarget(value) {
    if (!isRecord(value)) return invalid("INVALID_FIELD");
    if (!hasOnlyFields(value, ["nodeId", "expectedName", "newName"])) return invalid("UNKNOWN_FIELD");
    if (!isNonBlankString(value.nodeId) || !isNonBlankString(value.expectedName) || !isNonBlankString(value.newName)) {
      return invalid("INVALID_FIELD");
    }
    if (value.expectedName === value.newName) return invalid("INVALID_FIELD");
    return value;
  }
  function parseIconSwapTarget(value) {
    if (!isRecord(value)) return invalid("INVALID_FIELD");
    if (!hasOnlyFields(value, ["nodeId", "expectedMainComponentKey", "replacementComponentKey"])) {
      return invalid("UNKNOWN_FIELD");
    }
    if (!isNonBlankString(value.nodeId) || !isNonBlankString(value.expectedMainComponentKey) || !isNonBlankString(value.replacementComponentKey)) {
      return invalid("INVALID_FIELD");
    }
    if (value.expectedMainComponentKey === value.replacementComponentKey) return invalid("INVALID_FIELD");
    return value;
  }
  function parseMutationPlan(value, operation, parseTarget) {
    if (!hasOnlyFields(value, ["version", "mode", "operation", "targets"])) return invalid("UNKNOWN_FIELD");
    if (value.mode !== "preview" && value.mode !== "apply") return invalid("INVALID_FIELD");
    if (!Array.isArray(value.targets) || value.targets.length === 0) return invalid("INVALID_FIELD");
    const targets = [];
    const nodeIds = /* @__PURE__ */ new Set();
    for (const rawTarget of value.targets) {
      const target = parseTarget(rawTarget);
      if ("status" in target) return target;
      if (nodeIds.has(target.nodeId)) return invalid("DUPLICATE_TARGET");
      nodeIds.add(target.nodeId);
      targets.push(target);
    }
    return { version: 1, mode: value.mode, operation, targets };
  }
  function parsePlan(text) {
    let value;
    try {
      value = JSON.parse(text);
    } catch {
      return invalid("INVALID_JSON");
    }
    if (!isRecord(value)) return invalid("INVALID_FIELD");
    if (!hasOnlyFields(value, ["version", "mode", "operation", "scope", "targets"])) return invalid("UNKNOWN_FIELD");
    if (value.version !== 1) return invalid("UNSUPPORTED_VERSION");
    switch (value.operation) {
      case "inspect-selection":
      case "audit-auto-layout":
      case "audit-prototype-links":
        return parseReadOnlyPlan(value);
      case "rename-exact":
        return parseMutationPlan(value, "rename-exact", parseRenameTarget);
      case "replace-icon-instance-exact":
        return parseMutationPlan(value, "replace-icon-instance-exact", parseIconSwapTarget);
      default:
        return invalid("UNKNOWN_OPERATION");
    }
  }
  var isMutationPlan = (plan) => plan.operation === "rename-exact" || plan.operation === "replace-icon-instance-exact";
  var canonicalFingerprint = (plan) => {
    if (plan.operation === "rename-exact") {
      return JSON.stringify({ operation: plan.operation, targets: plan.targets.map((target) => {
        return {
          expectedName: target.expectedName,
          newName: target.newName,
          nodeId: target.nodeId
        };
      }) });
    }
    return JSON.stringify({ operation: plan.operation, targets: plan.targets.map((target) => ({
      expectedMainComponentKey: target.expectedMainComponentKey,
      nodeId: target.nodeId,
      replacementComponentKey: target.replacementComponentKey
    })) });
  };
  function aggregatePreview(results) {
    const ready = results.some((result) => result.status === "ready");
    const failed = results.some((result) => result.status === "failed");
    const skipped = results.some((result) => result.status === "skipped");
    if (failed && !ready) return "failed";
    if (ready && (failed || skipped)) return "partial";
    if (ready) return "ready";
    return "no_changes";
  }
  function aggregateApply(results) {
    const applied = results.some((result) => result.status === "applied");
    const failed = results.some((result) => result.status === "failed");
    const skipped = results.some((result) => result.status === "skipped");
    if (failed && !applied) return "failed";
    if (applied && (failed || skipped)) return "partial";
    if (applied) return "applied";
    return "no_changes";
  }
  function hasMatchingReceipt(receipt, plan) {
    if (!isRecord(receipt) || receipt.fingerprint !== canonicalFingerprint(plan) || !Array.isArray(receipt.targets)) return false;
    if (receipt.targets.length !== plan.targets.length) return false;
    return receipt.targets.every((candidate, index) => {
      if (!isRecord(candidate) || candidate.nodeId !== plan.targets[index].nodeId) return false;
      if (typeof candidate.disposition !== "string") return false;
      if (plan.operation === "rename-exact") {
        return candidate.expectedName === plan.targets[index].expectedName;
      }
      return candidate.expectedMainComponentKey === plan.targets[index].expectedMainComponentKey;
    });
  }
  var isAutoLayout = (layoutMode) => layoutMode === "HORIZONTAL" || layoutMode === "VERTICAL";
  var observedFields = (fields) => {
    const observed = {};
    for (const [key, value] of Object.entries(fields)) {
      if (value !== void 0) observed[key] = value;
    }
    return observed;
  };
  async function inspectOrAudit(plan, port) {
    const roots = await port.getSelection();
    if (roots.length === 0) return invalid("INVALID_FIELD");
    const nodes = JSON.parse(JSON.stringify(roots));
    if (plan.operation === "inspect-selection") return { status: "inspected", nodes };
    const flattened = [];
    const visit = (node, parent) => {
      const effectiveParent = node.parent ?? (parent && { id: parent.id, type: parent.type, layoutMode: parent.layoutMode });
      flattened.push({ node, parent: effectiveParent });
      for (const child of node.children ?? []) visit(child, node);
    };
    for (const root of nodes) visit(root);
    const findings = [];
    if (plan.operation === "audit-auto-layout") {
      for (const { node, parent } of flattened) {
        if ((node.layoutSizingHorizontal === "FILL" || node.layoutSizingVertical === "FILL") && !isAutoLayout(parent?.layoutMode)) {
          findings.push({
            code: "AUTO_LAYOUT_FILL_WITHOUT_AUTO_PARENT",
            nodeId: node.id,
            observed: observedFields({
              layoutSizingHorizontal: node.layoutSizingHorizontal,
              layoutSizingVertical: node.layoutSizingVertical,
              parentLayoutMode: parent?.layoutMode
            })
          });
        }
        if (node.layoutPositioning === "ABSOLUTE" && !isAutoLayout(parent?.layoutMode)) {
          findings.push({
            code: "AUTO_LAYOUT_ABSOLUTE_WITHOUT_AUTO_PARENT",
            nodeId: node.id,
            observed: observedFields({ layoutPositioning: node.layoutPositioning, parentLayoutMode: parent?.layoutMode })
          });
        }
      }
    } else {
      for (const { node } of flattened) {
        for (const [reactionIndex, reaction] of (node.reactions ?? []).entries()) {
          if (!reaction.actions || reaction.actions.length === 0) {
            findings.push({ code: "PROTOTYPE_EMPTY_ACTIONS", nodeId: node.id, observed: { reactionIndex: String(reactionIndex) } });
            continue;
          }
          for (const action of reaction.actions) {
            if (!action.destinationId) continue;
            if (await port.readNode(action.destinationId) === null) {
              findings.push({ code: "PROTOTYPE_DESTINATION_MISSING", nodeId: node.id, observed: { destinationId: action.destinationId } });
            }
          }
        }
      }
    }
    return { status: findings.length > 0 ? "findings" : "clean", findings };
  }
  async function previewPlan(text, port) {
    const parsed = parsePlan(text);
    if ("status" in parsed) return parsed;
    if (!isMutationPlan(parsed)) return inspectOrAudit(parsed, port);
    if (parsed.mode !== "preview") return invalid("INVALID_FIELD");
    const results = [];
    const receiptTargets = [];
    for (const target of parsed.targets) {
      let node;
      try {
        node = await port.readNode(target.nodeId);
      } catch {
        if (parsed.operation === "rename-exact") {
          receiptTargets.push({
            nodeId: target.nodeId,
            expectedName: target.expectedName,
            disposition: "LOOKUP_FAILED"
          });
        } else {
          receiptTargets.push({
            nodeId: target.nodeId,
            expectedMainComponentKey: target.expectedMainComponentKey,
            disposition: "LOOKUP_FAILED"
          });
        }
        results.push({ nodeId: target.nodeId, status: "failed", reason: "LOOKUP_FAILED" });
        continue;
      }
      if (parsed.operation === "rename-exact") {
        const renameTarget = target;
        if (node === null) {
          receiptTargets.push({ nodeId: target.nodeId, expectedName: renameTarget.expectedName, disposition: "MISSING_NODE" });
          results.push({ nodeId: target.nodeId, status: "skipped", reason: "MISSING_NODE" });
        } else if (node.name === renameTarget.newName) {
          receiptTargets.push({ nodeId: target.nodeId, expectedName: renameTarget.expectedName, observedName: node.name, disposition: "ALREADY_DESIRED" });
          results.push({ nodeId: target.nodeId, status: "skipped", reason: "ALREADY_DESIRED" });
        } else if (node.name !== renameTarget.expectedName) {
          receiptTargets.push({ nodeId: target.nodeId, expectedName: renameTarget.expectedName, observedName: node.name, disposition: "STALE_EXPECTED_STATE" });
          results.push({ nodeId: target.nodeId, status: "skipped", reason: "STALE_EXPECTED_STATE" });
        } else {
          receiptTargets.push({ nodeId: target.nodeId, expectedName: renameTarget.expectedName, observedName: node.name, disposition: "READY" });
          results.push({
            nodeId: target.nodeId,
            status: "ready",
            reason: "READY",
            before: { name: node.name },
            after: { name: renameTarget.newName }
          });
        }
        continue;
      }
      const iconTarget = target;
      if (node === null) {
        receiptTargets.push({ nodeId: target.nodeId, expectedMainComponentKey: iconTarget.expectedMainComponentKey, disposition: "MISSING_NODE" });
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "MISSING_NODE" });
      } else if (node.type !== "INSTANCE") {
        receiptTargets.push({ nodeId: target.nodeId, expectedMainComponentKey: iconTarget.expectedMainComponentKey, observedMainComponentKey: node.mainComponentKey, disposition: "WRONG_NODE_TYPE" });
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "WRONG_NODE_TYPE" });
      } else if (node.mainComponentKey === iconTarget.replacementComponentKey) {
        receiptTargets.push({ nodeId: target.nodeId, expectedMainComponentKey: iconTarget.expectedMainComponentKey, observedMainComponentKey: node.mainComponentKey, disposition: "ALREADY_DESIRED" });
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "ALREADY_DESIRED" });
      } else if (node.mainComponentKey !== iconTarget.expectedMainComponentKey) {
        receiptTargets.push({ nodeId: target.nodeId, expectedMainComponentKey: iconTarget.expectedMainComponentKey, observedMainComponentKey: node.mainComponentKey, disposition: "STALE_EXPECTED_STATE" });
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "STALE_EXPECTED_STATE" });
      } else {
        receiptTargets.push({ nodeId: target.nodeId, expectedMainComponentKey: iconTarget.expectedMainComponentKey, observedMainComponentKey: node.mainComponentKey, disposition: "READY" });
        results.push({
          nodeId: target.nodeId,
          status: "ready",
          reason: "READY",
          before: { mainComponentKey: node.mainComponentKey },
          after: { mainComponentKey: iconTarget.replacementComponentKey }
        });
      }
    }
    return {
      status: aggregatePreview(results),
      results,
      receipt: { fingerprint: canonicalFingerprint(parsed), targets: receiptTargets }
    };
  }
  async function applyPlan(text, receipt, port) {
    const parsed = parsePlan(text);
    if ("status" in parsed) return parsed;
    if (!isMutationPlan(parsed) || parsed.mode !== "apply") return invalid("INVALID_FIELD");
    if (receipt === void 0 || receipt === null) return invalid("PREVIEW_REQUIRED");
    if (!hasMatchingReceipt(receipt, parsed)) return invalid("PLAN_CHANGED");
    const results = [];
    for (const [index, target] of parsed.targets.entries()) {
      if (receipt.targets[index].disposition !== "READY") {
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "PREVIEW_NOT_READY" });
        continue;
      }
      let node;
      try {
        node = await port.readNode(target.nodeId);
      } catch {
        results.push({ nodeId: target.nodeId, status: "failed", reason: "LOOKUP_FAILED" });
        continue;
      }
      if (node === null) {
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "MISSING_NODE" });
        continue;
      }
      if (parsed.operation === "rename-exact") {
        const renameTarget = target;
        const beforeName = node.name;
        if (node.name === renameTarget.newName) {
          results.push({ nodeId: target.nodeId, status: "skipped", reason: "ALREADY_DESIRED" });
          continue;
        }
        if (node.name !== renameTarget.expectedName) {
          results.push({ nodeId: target.nodeId, status: "skipped", reason: "STALE_EXPECTED_STATE" });
          continue;
        }
        let mutation2;
        try {
          mutation2 = await port.renameIfCurrent(target.nodeId, renameTarget.expectedName, renameTarget.newName);
        } catch {
          results.push({ nodeId: target.nodeId, status: "failed", reason: "MUTATION_FAILED" });
          continue;
        }
        if (mutation2 === "missing") {
          results.push({ nodeId: target.nodeId, status: "skipped", reason: "MISSING_NODE" });
          continue;
        }
        if (mutation2 === "stale") {
          results.push({ nodeId: target.nodeId, status: "skipped", reason: "STALE_EXPECTED_STATE" });
          continue;
        }
        try {
          const readback = await port.readNode(target.nodeId);
          if (readback?.name === renameTarget.newName) {
            results.push({
              nodeId: target.nodeId,
              status: "applied",
              reason: "READY",
              before: { name: beforeName },
              after: { name: renameTarget.newName }
            });
          } else {
            results.push({ nodeId: target.nodeId, status: "failed", reason: "READBACK_MISMATCH", observed: observedFields({ name: readback?.name }) });
          }
        } catch {
          results.push({ nodeId: target.nodeId, status: "failed", reason: "READBACK_FAILED" });
        }
        continue;
      }
      const iconTarget = target;
      const beforeMainComponentKey = node.mainComponentKey;
      if (node.type !== "INSTANCE") {
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "WRONG_NODE_TYPE" });
        continue;
      }
      if (node.mainComponentKey === iconTarget.replacementComponentKey) {
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "ALREADY_DESIRED" });
        continue;
      }
      if (node.mainComponentKey !== iconTarget.expectedMainComponentKey) {
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "STALE_EXPECTED_STATE" });
        continue;
      }
      let component;
      try {
        component = await port.importComponent(iconTarget.replacementComponentKey);
      } catch {
        results.push({ nodeId: target.nodeId, status: "failed", reason: "IMPORT_FAILED" });
        continue;
      }
      let mutation;
      try {
        mutation = await port.replaceIconInstanceIfCurrent(
          target.nodeId,
          iconTarget.expectedMainComponentKey,
          component
        );
      } catch {
        results.push({ nodeId: target.nodeId, status: "failed", reason: "MUTATION_FAILED" });
        continue;
      }
      if (mutation === "missing") {
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "MISSING_NODE" });
        continue;
      }
      if (mutation === "stale") {
        results.push({ nodeId: target.nodeId, status: "skipped", reason: "STALE_EXPECTED_STATE" });
        continue;
      }
      try {
        const readback = await port.readNode(target.nodeId);
        if (readback?.mainComponentKey === iconTarget.replacementComponentKey) {
          results.push({
            nodeId: target.nodeId,
            status: "applied",
            reason: "READY",
            before: { mainComponentKey: beforeMainComponentKey },
            after: { mainComponentKey: iconTarget.replacementComponentKey }
          });
        } else {
          results.push({ nodeId: target.nodeId, status: "failed", reason: "READBACK_MISMATCH", observed: observedFields({ mainComponentKey: readback?.mainComponentKey }) });
        }
      } catch {
        results.push({ nodeId: target.nodeId, status: "failed", reason: "READBACK_FAILED" });
      }
    }
    return { status: aggregateApply(results), results };
  }

  // src/figma-adapter.ts
  var asRecord = (value) => typeof value === "object" && value !== null ? value : void 0;
  function readDestinationId(action) {
    const destinationId = asRecord(action)?.destinationId;
    return typeof destinationId === "string" ? destinationId : void 0;
  }
  function snapshotParent(parent) {
    const layoutMode = parent.layoutMode;
    return typeof layoutMode === "string" ? { id: parent.id, type: parent.type, layoutMode } : { id: parent.id, type: parent.type };
  }
  function snapshotVariableBindings(node) {
    const variableNode = node;
    const bindings = {};
    if (typeof variableNode.opacity === "number" && Number.isFinite(variableNode.opacity)) {
      bindings.opacity = { kind: "literal", value: variableNode.opacity };
    }
    const opacityBinding = asRecord(asRecord(variableNode.boundVariables)?.opacity);
    if (opacityBinding?.type === "VARIABLE_ALIAS" && typeof opacityBinding.id === "string") {
      bindings.opacity = { kind: "binding", variableId: opacityBinding.id };
    }
    return Object.keys(bindings).length > 0 ? bindings : void 0;
  }
  async function snapshotNode(node) {
    const namedNode = node;
    const layoutNode = node;
    const snapshot = {
      id: node.id,
      type: node.type,
      name: typeof namedNode.name === "string" ? namedNode.name : ""
    };
    if (node.type === "INSTANCE") {
      const mainComponent = await node.getMainComponentAsync();
      if (mainComponent) snapshot.mainComponentKey = mainComponent.key;
    }
    if (typeof layoutNode.layoutMode === "string") snapshot.layoutMode = layoutNode.layoutMode;
    if (typeof layoutNode.layoutSizingHorizontal === "string") {
      snapshot.layoutSizingHorizontal = layoutNode.layoutSizingHorizontal;
    }
    if (typeof layoutNode.layoutSizingVertical === "string") {
      snapshot.layoutSizingVertical = layoutNode.layoutSizingVertical;
    }
    if (typeof layoutNode.layoutPositioning === "string") {
      snapshot.layoutPositioning = layoutNode.layoutPositioning;
    }
    const parent = node.parent;
    if (parent) snapshot.parent = snapshotParent(parent);
    const variableBindings = snapshotVariableBindings(node);
    if (variableBindings) snapshot.variableBindings = variableBindings;
    const reactionNode = node;
    if (reactionNode.reactions) {
      snapshot.reactions = reactionNode.reactions.map((reaction) => {
        const actions = asRecord(reaction)?.actions;
        if (!Array.isArray(actions)) return {};
        return { actions: actions.map((action) => ({ destinationId: readDestinationId(action) })) };
      });
    }
    if ("children" in node) {
      const children = node.children;
      snapshot.children = await Promise.all(children.map(snapshotNode));
    }
    return snapshot;
  }
  var FigmaNodePort = class {
    async getSelection() {
      return Promise.all(figma.currentPage.selection.map(snapshotNode));
    }
    async readNode(nodeId) {
      const node = await figma.getNodeByIdAsync(nodeId);
      return node ? snapshotNode(node) : null;
    }
    async renameIfCurrent(nodeId, expectedName, name) {
      const node = await figma.getNodeByIdAsync(nodeId);
      if (!node) return "missing";
      if (!("name" in node) || node.name !== expectedName) return "stale";
      node.name = name;
      return "applied";
    }
    async importComponent(componentKey) {
      return figma.importComponentByKeyAsync(componentKey);
    }
    async replaceIconInstanceIfCurrent(nodeId, expectedMainComponentKey, component) {
      const node = await figma.getNodeByIdAsync(nodeId);
      if (!node) return "missing";
      if (node.type !== "INSTANCE") return "stale";
      if (!isComponentNode(component)) throw new Error("Imported value is not a component");
      const currentComponent = await node.getMainComponentAsync();
      if (currentComponent?.key !== expectedMainComponentKey) return "stale";
      node.swapComponent(component);
      return "applied";
    }
  };
  function isComponentNode(value) {
    const candidate = asRecord(value);
    return candidate?.type === "COMPONENT" && typeof candidate.key === "string";
  }

  // src/code.ts
  var invalidField = { status: "invalid", reason: "INVALID_FIELD" };
  var lookupFailed = { status: "invalid", reason: "LOOKUP_FAILED" };
  var isRequestId = (value) => typeof value === "number" && Number.isSafeInteger(value) && value >= 0;
  var isRequest = (value) => typeof value === "object" && value !== null;
  function createUiMessageHandler(port, post) {
    return async (message) => {
      let request = "invalid";
      let requestId = null;
      let input = null;
      let result = invalidField;
      try {
        if (isRequest(message) && (message.type === "preview" || message.type === "apply")) {
          request = message.type;
          if (typeof message.plan === "string" && typeof message.input === "string" && isRequestId(message.requestId)) {
            requestId = message.requestId;
            input = message.input;
            result = request === "preview" ? await previewPlan(message.plan, port) : await applyPlan(message.plan, message.receipt, port);
          }
        }
      } catch {
        result = request === "invalid" ? invalidField : lookupFailed;
      }
      post({ type: "result", request, requestId, input, result });
    };
  }
  function startPlugin() {
    const port = new FigmaNodePort();
    figma.showUI(__html__, { width: 520, height: 680, themeColors: true });
    figma.ui.onmessage = createUiMessageHandler(port, (message) => figma.ui.postMessage(message));
  }
  if (typeof figma !== "undefined" && typeof __html__ !== "undefined") startPlugin();
})();
