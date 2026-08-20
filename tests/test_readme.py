from __future__ import annotations

import unittest
from pathlib import Path


class ReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = Path("README.md").read_text(
            encoding="utf-8",
        )

    def test_readme_names_both_supported_platforms(self):
        self.assertIn(
            "Linux",
            self.readme,
        )
        self.assertIn(
            "Windows",
            self.readme,
        )

    def test_readme_documents_both_languages(self):
        self.assertIn(
            "Russian",
            self.readme,
        )
        self.assertIn(
            "English",
            self.readme,
        )

    def test_readme_documents_windows_delete_omission(self):
        self.assertIn(
            "Windows file deletion is not exposed",
            self.readme,
        )

    def test_readme_documents_windows_installer_and_verifier(self):
        self.assertIn(
            r".\windows\install_windows.ps1",
            self.readme,
        )
        self.assertIn(
            r".\windows\verify_windows.ps1",
            self.readme,
        )

    def test_readme_documents_config_override(self):
        self.assertIn(
            "IR_CONFIG",
            self.readme,
        )

    def test_readme_marks_windows_live_validation_complete(self):
        self.assertIn(
            "Windows live validation is complete for the current 8-command voice surface.",
            self.readme,
        )
