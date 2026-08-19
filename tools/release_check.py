from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "PUBLIC_PORTING_NOTES.md",
    "WINDOWS_LIVE_VALIDATION_2026-08-19.md",
    "config.linux.example.json",
    "config.windows.example.json",
    "windows/install_windows.ps1",
    "windows/uninstall_windows_autostart.ps1",
    "windows/verify_windows.ps1",
)

EXPECTED_VERSION = "0.1.0"


def fail(message: str) -> None:
    raise SystemExit(f"RELEASE CHECK FAILED: {message}")


def run(
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def main() -> int:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]

    if missing:
        fail("missing files: " + ", ".join(missing))

    data = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(
            encoding="utf-8",
        )
    )

    version = data["project"]["version"]

    if version != EXPECTED_VERSION:
        fail(f"unexpected version: {version}")

    status = run(
        "git",
        "status",
        "--porcelain",
    )

    if status.returncode != 0:
        fail(status.stderr.strip() or "git status failed")

    if status.stdout.strip():
        fail("worktree is not clean")

    branch = run(
        "git",
        "branch",
        "--show-current",
    )

    if branch.returncode != 0:
        fail(branch.stderr.strip() or "cannot read branch")

    if branch.stdout.strip() != "main":
        fail("release candidate must be on main")

    print("IR PUBLIC RELEASE READINESS: PASS")
    print(f"VERSION: {version}")
    print("BRANCH: main")
    print("REQUIRED FILES: PASS")
    print("WORKTREE: CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
