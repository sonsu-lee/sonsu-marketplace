"""Check that auxiliary requests cannot satisfy omp prompt loading."""

import json
from pathlib import Path
import sys
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from check_plugins import Receiver  # noqa: E402


class PluginLoadingTests(unittest.TestCase):
    def setUp(self):
        self.receiver = Receiver()
        self.addCleanup(self.receiver.close)

    def post(self, *messages):
        payload = json.dumps({"messages": [{"content": msg} for msg in messages]}).encode()
        request = Request(f"http://127.0.0.1:{self.receiver.port}/v1", data=payload)
        with self.assertRaises(HTTPError) as error:
            urlopen(request, timeout=5)
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_auxiliary_request_then_complete_invocation(self):
        self.post("Compress into one routing hint")
        self.assertFalse(self.receiver.contains("check-unique"))
        self.post("check-unique", "Complete skill\nbody")
        self.assertTrue(self.receiver.request_contains("check-unique", "Complete skill body"))

    def test_missing_or_truncated_invocation_body_is_not_satisfied_by_another_request(self):
        self.post("Complete skill body")
        self.post("check-unique", "Complete skill")
        self.assertFalse(self.receiver.request_contains("check-unique", "Complete skill body"))
        self.assertFalse(self.receiver.request_contains("missing-marker", "Complete skill body"))

    def test_renderer_table_separator_compaction_preserves_complete_loading(self):
        expected = "# Guide\n| Name | Purpose |\n| -------- | ------------ |\n| Read | Inspect |\nEnd."
        received = "# Guide\n|Name|Purpose|\n|---|---|\n|Read|Inspect|\nEnd."
        self.post("table-probe", received)
        self.assertTrue(self.receiver.request_contains("table-probe", expected))
        self.receiver.reset()
        self.post("table-probe", received.removesuffix("End."))
        self.assertFalse(self.receiver.request_contains("table-probe", expected))

    def test_table_alignment_and_literal_cell_content_are_not_normalized_away(self):
        expected = "| Name | Value |\n| :------ | ------: |\n| ---- | ----- |\nEnd."
        for received in (
            "| Name | Value |\n| ------: | :------ |\n| ---- | ----- |\nEnd.",
            "| Name | Value |\n| :------ | ------: |\n| --- | --- |\nEnd.",
        ):
            with self.subTest(received=received):
                self.receiver.reset()
                self.post("table-probe", received)
                self.assertFalse(self.receiver.request_contains("table-probe", expected))

    def test_table_like_code_is_not_rewritten(self):
        expected = "```md\n| Name | Value |\n| -------- | -------- |\n```\nEnd."
        received = "```md\n| Name | Value |\n| --- | --- |\n```\nEnd."
        self.post("code-probe", received)
        self.assertFalse(self.receiver.request_contains("code-probe", expected))


    def test_indented_code_cannot_supply_a_table_header(self):
        expected = "    | Name | Value |\n| -------- | -------- |\nEnd."
        received = "    | Name | Value |\n| --- | --- |\nEnd."
        self.post("indented-probe", received)
        self.assertFalse(self.receiver.request_contains("indented-probe", expected))


if __name__ == "__main__":
    unittest.main()
