import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import runner


class IsolationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(HOME=str(self.root), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

    def git(self, root, *args):
        return subprocess.run(["git", "-C", str(root), *args], env=self.env,
                              text=True, capture_output=True, check=True).stdout.strip()

    def repository(self, name):
        root = self.root / name
        root.mkdir()
        (root / "tracked.txt").write_text(name)
        self.git(root, "-c", "init.templateDir=", "init", "-q")
        self.git(root, "add", ".")
        self.git(root, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "commit", "-qm", name)
        return root

    def test_fixture_initialization_does_not_modify_inherited_repository(self):
        external = self.repository("external")
        fixture = self.root / "fixture"
        fixture.mkdir()
        (fixture / "fixture.txt").write_text("fixture")
        (external / "untracked.txt").write_text("must stay untracked")
        before_head = self.git(external, "rev-parse", "HEAD")
        before_index = (external / ".git/index").read_bytes()
        before_config = (external / ".git/config").read_bytes()
        with mock.patch.dict(os.environ, {**self.env, "GIT_DIR": str(external / ".git"),
                             "GIT_WORK_TREE": str(external), "GIT_INDEX_FILE": str(external / ".git/index")}, clear=True):
            runner._initialize_fixture_git(fixture)
        self.assertEqual(self.git(external, "rev-parse", "HEAD"), before_head)
        self.assertEqual((external / ".git/index").read_bytes(), before_index)
        self.assertEqual((external / ".git/config").read_bytes(), before_config)
        self.assertTrue((fixture / ".git/HEAD").is_file())
        self.assertEqual(self.git(fixture, "ls-files"), "fixture.txt")

    def test_fixture_initialization_does_not_write_inherited_git_config(self):
        external = self.repository("external")
        config = external / ".git/config"
        self.git(external, "config", "user.name", "Original User")
        before = config.read_bytes()
        fixture = self.root / "fixture"
        fixture.mkdir()
        (fixture / "fixture.txt").write_text("fixture")
        with mock.patch.dict(os.environ, {**self.env, "GIT_CONFIG": str(config)}, clear=True):
            runner._initialize_fixture_git(fixture)
        self.assertEqual(config.read_bytes(), before)
        self.assertEqual(self.git(fixture, "config", "user.name"), "Marketplace Eval")
        self.assertEqual(self.git(fixture, "ls-files"), "fixture.txt")

    def test_candidate_revision_ignores_inherited_repository(self):
        candidate = self.repository("candidate")
        external = self.repository("external")
        expected = self.git(candidate, "rev-parse", "HEAD")
        with mock.patch.dict(os.environ, {**self.env, "GIT_DIR": str(external / ".git"),
                             "GIT_WORK_TREE": str(external)}, clear=True):
            self.assertEqual(runner._git_revision(candidate), expected)

    def test_isolated_child_environment_removes_only_repository_git_overrides(self):
        auth = self.root / "auth"
        auth.mkdir()
        (auth / "auth.json").write_text("{}")
        overrides = {key: "/unrelated" for key in (
            "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX",
            "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
            "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT", "GIT_IMPLICIT_WORK_TREE",
            "GIT_GRAFT_FILE", "GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE", "GIT_SHALLOW_FILE",
            "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0",
        )}
        with mock.patch.dict(os.environ, {**self.env, **overrides, "CODEX_HOME": str(auth),
                             "GIT_TERMINAL_PROMPT": "0", "EVAL_LABEL": "keep"}, clear=True):
            env = runner._isolated_environment(self.root / "run")
        self.assertFalse(set(overrides) & set(env))
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        self.assertEqual(env["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertEqual(env["EVAL_LABEL"], "keep")

    def test_prepare_rejects_candidate_descendants_before_validation_or_creation(self):
        candidate = self.root / "candidate"
        candidate.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(candidate, target_is_directory=True)
        for candidate_arg, output in (
            (candidate, candidate / "new/output"), (candidate, alias / "linked/output"),
            (alias, candidate / "resolved/output"), (candidate, candidate),
        ):
            with self.subTest(candidate=candidate_arg, output=output):
                with mock.patch.object(runner, "validate_sources", side_effect=AssertionError("validation reached")) as validate:
                    with self.assertRaises(runner.EvaluationError):
                        runner.prepare(output, candidate_arg, self.root / "unused")
                validate.assert_not_called()
                self.assertEqual(list(candidate.iterdir()), [])

    def test_prepare_accepts_external_output_for_alternate_candidate(self):
        candidate = self.repository("candidate")
        binary = self.root / "codex"
        binary.write_text("fake binary")
        source = {"profiles": [], "cases": {"cases": []}, "cohorts": {}}
        with mock.patch.object(runner, "validate_sources", return_value=source), \
             mock.patch.object(runner, "_run_matrix", return_value=[]), \
             mock.patch.object(runner, "_node_runtime_record", return_value={}), \
             mock.patch.object(runner, "_codex_version", return_value="fake"), \
             mock.patch.dict(os.environ, self.env, clear=True):
            manifest = runner.prepare(self.root / "output", candidate, binary)
        self.assertEqual(manifest["candidate_git_revision"], self.git(candidate, "rev-parse", "HEAD"))
        self.assertTrue((self.root / "output/manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
