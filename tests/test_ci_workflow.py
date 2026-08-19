from __future__ import annotations

import unittest
from pathlib import Path


class CIWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = Path(".github/workflows/ci.yml").read_text(
            encoding="utf-8",
        )

    def test_ci_runs_on_linux_and_windows(self):
        self.assertIn(
            "ubuntu-latest",
            self.workflow,
        )
        self.assertIn(
            "windows-latest",
            self.workflow,
        )

    def test_ci_uses_python_312(self):
        self.assertIn(
            '"3.12"',
            self.workflow,
        )

    def test_windows_installs_windows_extra(self):
        self.assertIn(
            'python -m pip install -e ".[dev,windows]"',
            self.workflow,
        )

    def test_ci_runs_ruff_and_tests(self):
        self.assertIn(
            "python -m ruff check argo tests tools",
            self.workflow,
        )
        self.assertIn(
            "python -m unittest discover -v",
            self.workflow,
        )
