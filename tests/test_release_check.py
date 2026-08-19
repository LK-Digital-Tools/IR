from __future__ import annotations

import unittest
from pathlib import Path


class ReleaseCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = Path("tools/release_check.py").read_text(
            encoding="utf-8",
        )

    def test_gate_requires_cross_platform_docs(self):
        self.assertIn(
            "README.md",
            self.text,
        )
        self.assertIn(
            "WINDOWS_LIVE_VALIDATION_2026-08-19.md",
            self.text,
        )

    def test_gate_requires_both_platform_configs(self):
        self.assertIn(
            "config.linux.example.json",
            self.text,
        )
        self.assertIn(
            "config.windows.example.json",
            self.text,
        )

    def test_gate_requires_windows_installer_and_verifier(self):
        self.assertIn(
            "windows/install_windows.ps1",
            self.text,
        )
        self.assertIn(
            "windows/verify_windows.ps1",
            self.text,
        )

    def test_gate_requires_version_0_1_0(self):
        self.assertIn(
            'EXPECTED_VERSION = "0.1.0"',
            self.text,
        )

    def test_gate_requires_main_and_clean_worktree(self):
        self.assertIn(
            '"branch",',
            self.text,
        )
        self.assertIn(
            '"--show-current",',
            self.text,
        )
        self.assertIn(
            "worktree is not clean",
            self.text,
        )
