#!/usr/bin/env python3
"""Read-only structural validator for plans in skills/plan/references/plan-format.md.

Usage: validate_plan.py PLAN --root REPOSITORY
Prints JSON: status, plan, root, flows, tasks, mappings, files, errors.
Exit 0: structurally valid; 1: plan findings; 2: input/CLI error (argparse
usage errors use stderr). Does not run commands or judge approval, requirements,
verification quality, or readiness. Create paths may be absent; Modify and Verify
paths must be existing files or have an explicit Create declaration.
"""

import argparse
import json
from pathlib import Path
import re
import sys


# ASCII boundaries: Korean particles such as `F9에서` and `Task 7의` still reference IDs.
FLOW = re.compile(r"(?<![\w-])F[1-9][0-9]*(?![\w-])", re.ASCII)
TASK = re.compile(r"\bTask\s+([1-9][0-9]*)\b", re.ASCII)
FLOW_DEF = re.compile(r"^FLOW (F[1-9][0-9]*):\s*\S")
TASK_DEF = re.compile(r"^#{1,6}\s+Task ([1-9][0-9]*):\s*\S")
HEADER = ["흐름", "요구사항", "입력과 결과", "파일과 책임", "작업과 의존 관계", "검증과 이유"]


def validate(text, root):
    errors = []
    flows = {}
    tasks = {}
    mappings = []
    files = []
    references = []
    current = None
    in_files = False
    table = False
    fence = None
    flow_fence = False

    def error(code, line, message):
        errors.append({"code": code, "line": line, "message": message})

    def ids(value, pattern, line, kind):
        found = pattern.findall(value)
        if len(found) != len(set(found)):
            error("duplicate_reference", line, f"Repeated {kind} ID in one field")
        return found

    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        fence_match = re.match(r"^(`{3,}|~{3,})(.*)$", line)
        if fence_match:
            marker, info = fence_match.groups()
            if fence is None:
                fence = marker
                flow_fence = info.strip() in ("", "text")
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not info.strip():
                fence = None
                flow_fence = False
            continue
        if fence and not flow_fence:
            continue
        definition = FLOW_DEF.match(line)
        if definition:
            flow_id = definition.group(1)
            if flow_id in flows:
                error("duplicate_flow", line_no, f"{flow_id} already defined at line {flows[flow_id]}")
            else:
                flows[flow_id] = line_no
        elif line.startswith("FLOW "):
            error("invalid_flow", line_no, "Expected FLOW F<positive integer>: description")
        if fence:
            # Text fences contain flow pseudocode, not task declarations or tables.
            if flow_fence:
                references.extend(("flow", value, line_no) for value in FLOW.findall(line))
            continue

        # IDs in prose and inline ID code are references; file paths are not.
        prose = re.sub(r"`([^`]*)`", lambda span: "" if re.search(r"[./\\]", span.group(1)) else span.group(0), line)
        references.extend(("flow", value, line_no) for value in FLOW.findall(prose))
        references.extend(("task", value, line_no) for value in TASK.findall(prose))
        heading = TASK_DEF.match(line)
        if heading:
            task_id = heading.group(1)
            depth = len(line) - len(line.lstrip("#"))
            current = {"id": task_id, "line": line_no, "depth": depth, "flows": [], "flow_fields": 0, "files": []}
            if task_id in tasks:
                error("duplicate_task", line_no, f"Task {task_id} already defined at line {tasks[task_id]['line']}")
            else:
                tasks[task_id] = current
            in_files = False
            table = False
            continue
        if re.match(r"^#{1,6}\s+Task\b", line):
            error("invalid_task", line_no, "Expected heading Task <positive integer>: description")
            current = None
            in_files = False
        heading_match = re.match(r"^(#{1,6})\s", line)
        if heading_match:
            heading_depth = len(heading_match.group(1))
            in_files = False
            table = False
            # A same-or-higher level heading ends the task; deeper headings stay inside it.
            if current is not None and heading_depth <= current["depth"]:
                current = None

        flow_field = re.match(r"^\*\*Flows:\*\*\s*(.*)$", line)
        if flow_field and current is None:
            error("flows_without_task", line_no, "Flows must belong to a Task heading")
        elif flow_field:
            current["flow_fields"] += 1
            current["flows"].extend(ids(flow_field.group(1), FLOW, line_no, "flow"))
            remainder = FLOW.sub("", flow_field.group(1)).strip(" `,;")
            if remainder or not current["flows"]:
                error("invalid_flows", line_no, "Flows must contain only F IDs separated by spaces, commas or semicolons")
        if line == "**Files:**":
            in_files = current is not None
            if current is None:
                error("files_without_task", line_no, "Files must belong to a Task heading")
            continue
        if line.startswith("**"):
            in_files = False
        if in_files and line:
            declaration = re.fullmatch(r"- (Create|Modify|Verify): `([^`]+)`", line)
            if not declaration:
                error("invalid_file_declaration", line_no, "Expected - Create|Modify|Verify: `relative/path[:line[-line]]`")
            else:
                action, location = declaration.groups()
                path = re.sub(r":[1-9][0-9]*(?:-[1-9][0-9]*)?$", "", location)
                entry = {"task": current["id"], "action": action, "path": path, "line": line_no}
                current["files"].append(entry)
                files.append(entry)
            continue
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells == HEADER:
                table = True
                continue
            if table and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            if table:
                if len(cells) != 6 or any(not cell for cell in cells):
                    error("invalid_mapping", line_no, "Mapping rows require six nonempty cells")
                    continue
                flow_ids = ids(cells[0], FLOW, line_no, "flow")
                # Before the first semicolon: owning tasks; after it: dependencies.
                task_ids = ids(cells[4].split(";", 1)[0], TASK, line_no, "task")
                if not flow_ids or not task_ids or FLOW.sub("", cells[0]).strip(" `,"):
                    error("invalid_mapping", line_no, "Mapping requires flow IDs and owning Task IDs before any semicolon")
                for flow_id in flow_ids:
                    for task_id in task_ids:
                        mappings.append({"flow": flow_id, "task": task_id, "line": line_no})
            continue
        if line:
            table = False

    if fence:
        error("unclosed_fence", len(text.splitlines()), "Close the fenced code block")
    if not flows:
        error("missing_flows", 0, "No FLOW definitions")
    if not tasks:
        error("missing_tasks", 0, "No Task headings")
    if not mappings:
        error("missing_mappings", 0, "No flow/task mapping rows")
    seen_references = set()
    for kind, value, line_no in references:
        if value not in (flows if kind == "flow" else tasks) and (kind, value, line_no) not in seen_references:
            error("dangling_" + kind, line_no, f"Undefined {kind} {value}")
            seen_references.add((kind, value, line_no))
    pairs = set()
    for mapping in mappings:
        pair = (mapping["flow"], mapping["task"])
        if pair in pairs:
            error("duplicate_mapping", mapping["line"], f"Repeated mapping {pair[0]} / Task {pair[1]}")
        pairs.add(pair)
        task = tasks.get(mapping["task"])
        if task is not None and mapping["flow"] not in task["flows"]:
            error("mapping_not_in_task", mapping["line"], f"Task {task['id']} does not declare {mapping['flow']}")
    for flow_id, line_no in flows.items():
        if not any(flow == flow_id for flow, _ in pairs):
            error("unmapped_flow", line_no, f"{flow_id} has no task mapping")
    for task_id, task in tasks.items():
        if task["flow_fields"] != 1 or not task["flows"]:
            error("missing_or_duplicate_flows_field", task["line"], f"Task {task_id} requires one nonempty Flows field")
        if not task["files"]:
            error("missing_files", task["line"], f"Task {task_id} has no file declarations")
        if not any(mapped_task == task_id for _, mapped_task in pairs):
            error("unmapped_task", task["line"], f"Task {task_id} has no flow mapping")
        for flow_id in task["flows"]:
            if (flow_id, task_id) not in pairs:
                error("missing_mapping", task["line"], f"{flow_id} / Task {task_id} is absent from mapping table")

    creates = set()
    seen_files = set()
    for entry in files:
        path = Path(entry["path"])
        resolved = (root / path).resolve()
        if path.is_absolute() or ".." in path.parts or resolved == root or not resolved.is_relative_to(root):
            error("invalid_path", entry["line"], f"Path must stay inside root: {entry['path']}")
            entry["exists"] = False
            continue
        entry["exists"] = resolved.is_file()
        entry["resolved"] = str(resolved)
        key = (entry["task"], entry["action"], resolved)
        if key in seen_files:
            error("duplicate_file", entry["line"], f"Repeated {entry['action']} declaration: {entry['path']}")
        seen_files.add(key)
        if entry["action"] == "Create":
            creates.add(resolved)
        if resolved.exists() and not resolved.is_file():
            error("not_a_file", entry["line"], f"Declared path is not a file: {entry['path']}")
            del entry["resolved"]
    for entry in files:
        if "resolved" not in entry:
            continue
        resolved = Path(entry["resolved"])
        if entry["action"] in ("Modify", "Verify") and not entry["exists"] and resolved not in creates:
            error("missing_file", entry["line"], f"{entry['action']} requires an existing file or explicit Create declaration: {entry['path']}")
        entry["planned_new"] = resolved in creates
        del entry["resolved"]
    return {"status": "invalid" if errors else "valid", "flows": list(flows),
            "tasks": list(tasks), "mappings": mappings, "files": files, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="UTF-8 Markdown plan")
    parser.add_argument("--root", type=Path, required=True, help="repository root for declared file paths")
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("--root must be a directory")
        text = args.plan.read_text(encoding="utf-8")
        result = validate(text, root)
        result.update(plan=str(args.plan.resolve()), root=str(root))
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "input_error", "errors": [{"code": "input_error", "line": 0, "message": str(exc)}]}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
