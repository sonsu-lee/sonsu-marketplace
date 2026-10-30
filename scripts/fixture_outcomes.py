"""Deterministic outcome checks for local mechanical-change fixtures."""

import ast
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize


_CASES = frozenset({
    "bulk-rename", "imports", "shadowing", "mixed-syntax", "parse-error",
    "tiny", "preview", "executing-csv",
})


def _files(root):
    files = set()
    for directory, dirs, names in os.walk(root, followlinks=False):
        directory = Path(directory)
        for name in dirs + names:
            path = directory / name
            if path.is_symlink():
                raise ValueError(f"symlink is not allowed: {path.relative_to(root)}")
        if directory == root and ".git" in dirs:
            dirs.remove(".git")
        for name in names:
            path = directory / name
            if not path.is_file():
                raise ValueError(f"unsupported filesystem entry: {path.relative_to(root)}")
            files.add(path.relative_to(root).as_posix())
    return files

def _comments(source):
    return [token.string for token in tokenize.generate_tokens(io.StringIO(source).readline)
            if token.type == tokenize.COMMENT]


def _grade_csv(input_dir, output_dir):
    errors = []
    try:
        if input_dir.is_symlink() or output_dir.is_symlink():
            raise ValueError("fixture roots must not be symlinks")
        inputs, actual = _files(input_dir), _files(output_dir)
        actual = {name for name in actual
                  if not (Path(name).parts[0] == "__pycache__" and name.endswith(".pyc"))}
        if inputs != {"exporter.py", "test_exporter.py"} or actual != inputs:
            return ["CSV fixture file inventory differs"]
        test_source = (output_dir / "test_exporter.py").read_text()
        if test_source == (input_dir / "test_exporter.py").read_text():
            errors.append("CSV tests were not updated")
        tree = ast.parse(test_source)
        strings = [node.value for node in ast.walk(tree)
                   if isinstance(node, ast.Constant) and isinstance(node.value, str)]
        if not any("," in value for value in strings) or not any('"' in value for value in strings):
            errors.append("CSV tests do not cover both commas and quotes")
    except (OSError, UnicodeError, SyntaxError, ValueError) as exc:
        return [f"cannot inspect CSV fixture: {exc}"]
    sandbox = shutil.which("sandbox-exec")
    if sys.platform != "darwin" or not sandbox:
        return errors + ["CSV behavior unverified: macOS sandbox-exec unavailable"]
    with tempfile.TemporaryDirectory(prefix="fixture-csv-") as home:
        home = str(Path(home).resolve())
        checked = Path(home) / "workspace"
        checked.mkdir()
        for name in inputs:
            shutil.copyfile(output_dir / name, checked / name)
        profile = ('(version 1)(allow default)(deny network*)'
                   '(deny file-write*)(allow file-write* (subpath '
                   + json.dumps(home) + '))')
        script = """
import csv, io, sys, unittest
sys.path.insert(0, sys.argv[1])
from exporter import export_csv
rows = [["alice", "active"], ["a,b", 'say "hello"']]
result = export_csv(rows)
assert isinstance(result, str), "export_csv must return a string"
assert list(csv.reader(io.StringIO(result, newline=""), strict=True)) == rows
assert export_csv([["alice", "active"]]) == "alice,active\\n"
suite = unittest.defaultTestLoader.discover(sys.argv[1], pattern="test_exporter.py")
assert suite.countTestCases() > 0, "no fixture tests discovered"
assert unittest.TextTestRunner().run(suite).wasSuccessful(), "fixture tests failed"
"""
        try:
            result = subprocess.run(
                [sandbox, "-p", profile, sys.executable, "-I", "-B", "-c",
                 script, str(checked)],
                cwd=home, env={"HOME": home, "TMPDIR": home, "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=20,
            )
            if result.returncode:
                errors.append("CSV behavior or tests failed: " + result.stderr[-2000:])
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"CSV behavior unverified: {exc}")
    return errors

def grade(case_id, input_dir, output_dir, final_text):
    """Return errors; modified code is compared structurally, other files exactly."""
    if case_id not in _CASES:
        raise ValueError(f"unknown fixture outcome: {case_id}")
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    if case_id == "executing-csv":
        return _grade_csv(input_dir, output_dir)
    fixture = input_dir.parent
    expected = fixture / "expected"
    modified = set(json.loads((fixture / "outcome.json").read_text())["modified"])
    errors = []
    try:
        if input_dir.is_symlink() or output_dir.is_symlink():
            raise ValueError("fixture roots must not be symlinks")
        inputs, actual, wanted = _files(input_dir), _files(output_dir), _files(expected)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    if inputs != wanted:
        errors.append("input fixture does not match expected file inventory")
    if actual != wanted:
        errors.append(f"file inventory differs: missing={sorted(wanted - actual)}, extra={sorted(actual - wanted)}")
    for name in sorted(actual & wanted):
        try:
            got = (output_dir / name).read_bytes()
            target = (expected / name).read_bytes()
            if name not in modified:
                if got != (input_dir / name).read_bytes() or got != target:
                    errors.append(f"untouched file changed: {name}")
            elif name.endswith(".py"):
                source, expected_source = got.decode("utf-8"), target.decode("utf-8")
                if ast.dump(ast.parse(source), include_attributes=False) != ast.dump(ast.parse(expected_source), include_attributes=False):
                    errors.append(f"Python outcome differs: {name}")
                if _comments(source) != _comments(expected_source):
                    errors.append(f"Python comments changed: {name}")
            elif name.endswith(".json"):
                if json.loads(got) != json.loads(target):
                    errors.append(f"JSON outcome differs: {name}")
            else:
                errors.append(f"unsupported modified file type: {name}")
        except (OSError, UnicodeError, SyntaxError, tokenize.TokenError, ValueError) as exc:
            errors.append(f"cannot compare {name}: {exc}")
    if case_id == "parse-error":
        if "broken.py" not in final_text or not re.search(r"\b(?:parse|parsing|syntax|error|invalid)\b", final_text, re.I):
            errors.append("report must identify broken.py and its parse error")
    if case_id == "preview":
        if not all(word in final_text for word in ("timeout_ms", "request_timeout_ms", "a.py", "b.py")):
            errors.append("preview must identify both files and the proposed rename")
    return errors
