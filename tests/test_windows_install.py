from __future__ import annotations

import unittest
from pathlib import Path


class WindowsInstallTests(unittest.TestCase):
    def setUp(self):
        self.install = Path("windows/install_windows.ps1").read_text(
            encoding="utf-8",
        )
        self.uninstall = Path("windows/uninstall_windows_autostart.ps1").read_text(
            encoding="utf-8",
        )

    def test_installer_creates_venv_and_windows_extra(self):
        self.assertIn(
            "python -m venv",
            self.install,
        )
        self.assertIn(
            'pip install -e "$Project[windows]"',
            self.install,
        )

    def test_installer_uses_appdata_config(self):
        self.assertIn(
            '$env:APPDATA "IR"',
            self.install,
        )
        self.assertIn(
            "config.windows.example.json",
            self.install,
        )

    def test_autostart_runs_pythonw_at_logon(self):
        self.assertIn(
            "New-ScheduledTaskAction",
            self.install,
        )
        self.assertIn(
            "-Execute $Pythonw",
            self.install,
        )
        self.assertIn(
            "New-ScheduledTaskTrigger",
            self.install,
        )
        self.assertIn(
            "-AtLogOn",
            self.install,
        )
        self.assertIn(
            "-User $env:USERNAME",
            self.install,
        )

    def test_autostart_does_not_request_system_or_admin_context(self):
        self.assertNotIn(
            "-RunLevel Highest",
            self.install,
        )
        self.assertNotIn(
            "-User SYSTEM",
            self.install,
        )

    def test_uninstaller_only_removes_autostart_task(self):
        self.assertIn(
            "Unregister-ScheduledTask",
            self.uninstall,
        )
        self.assertNotIn(
            "Remove-Item",
            self.uninstall,
        )
