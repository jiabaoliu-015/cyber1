#!/usr/bin/env python3
"""Regression checks for the rubric-first challenge catalogue."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "challenges" / "manifest.json"
RUNNER = ROOT / "tools" / "challenge"


class ChallengeCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text())
        cls.required = [x for x in cls.data["challenges"] if not x.get("optional")]

    def test_required_inventory_and_lab_counts(self):
        self.assertEqual(17, len(self.required))
        expected = {"network": 3, "web": 6, "privilege-escalation": 3, "offline-artefacts": 5}
        actual = {lab: sum(x["lab"] == lab for x in self.required) for lab in expected}
        self.assertEqual(expected, actual)

    def test_required_challenges_are_independent_and_unique(self):
        self.assertTrue(all(not x["depends_on"] for x in self.required))
        self.assertEqual(len(self.required), len({x["id"] for x in self.required}))
        self.assertEqual(len(self.required), len({x["receipt_id"] for x in self.required}))

    def test_completion_is_the_only_aggregate_step(self):
        self.assertEqual({x["id"] for x in self.required}, set(self.data["completion"]["depends_on"]))

    def test_catalogue_command_validates(self):
        result = subprocess.run([sys.executable, str(RUNNER), "validate"], text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
