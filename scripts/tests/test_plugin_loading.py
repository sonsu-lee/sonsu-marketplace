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


if __name__ == "__main__":
    unittest.main()
