import unittest

from exporter import export_csv


class ExporterTest(unittest.TestCase):
    def test_simple_rows(self):
        self.assertEqual(export_csv([["alice", "active"]]), "alice,active\n")


if __name__ == "__main__":
    unittest.main()
