from __future__ import annotations

import unittest
from pathlib import Path


class WindowsVerifierTests(unittest.TestCase):
    def setUp(self):
        self.script = Path("windows/verify_windows.ps1").read_text(
            encoding="utf-8",
        )

    def test_verifier_runs_full_test_suite(self):
        self.assertIn(
            "-m unittest discover -v",
            self.script,
        )

    def test_verifier_checks_windows_media_dependencies(self):
        self.assertIn(
            "winrt.windows.media.control",
            self.script,
        )
        self.assertIn(
            "pycaw.pycaw",
            self.script,
        )

    def test_verifier_checks_voice_dependencies(self):
        self.assertIn(
            "import sounddevice",
            self.script,
        )
        self.assertIn(
            "import vosk",
            self.script,
        )

    def test_verifier_checks_config(self):
        self.assertIn(
            "$env:APPDATA",
            self.script,
        )
        self.assertIn(
            "$env:IR_CONFIG = $Config",
            self.script,
        )
        self.assertIn(
            "load_config",
            self.script,
        )

    def test_verifier_checks_windows_action_surface(self):
        self.assertIn(
            "get_supported_actions(platform='win32')",
            self.script,
        )
        self.assertIn(
            "'delete_current' not in actions",
            self.script,
        )

    def test_verifier_checks_audio_devices(self):
        self.assertIn(
            "sd.query_devices()",
            self.script,
        )

    def test_verifier_contains_foundation_import(
        self,
    ):
        self.assertIn(
            "winrt.windows.foundation",
            self.script,
        )

    def test_verifier_contains_foundationcollections_import(
        self,
    ):
        self.assertIn(
            "winrt.windows.foundation.collections",
            self.script,
        )

    def test_verifier_contains_gsmtc_manager_request(
        self,
    ):
        self.assertIn(
            "request_async()",
            self.script,
        )

    def test_verifier_contains_gsmtc_session_reporting(
        self,
    ):
        self.assertIn(
            "GSMTC SESSIONS:",
            self.script,
        )

    def test_verifier_contains_fallback_note(
        self,
    ):
        self.assertIn(
            "WM_APPCOMMAND fallback",
            self.script,
        )
