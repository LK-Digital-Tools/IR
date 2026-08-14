from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path


def _expand(value):
    if isinstance(value, str):
        expanded = Path(value).expanduser() if value.startswith("~") else value
        return os.path.expandvars(str(expanded))

    if isinstance(value, list):
        return [_expand(item) for item in value]

    if isinstance(value, dict):
        return {key: _expand(item) for key, item in value.items()}

    return value


def default_config_path(
    *,
    platform: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    env = os.environ if environ is None else environ

    override = env.get("IR_CONFIG")

    if override:
        return Path(override).expanduser()

    target = sys.platform if platform is None else platform

    if target == "win32":
        appdata = env.get("APPDATA")

        if appdata:
            return Path(appdata) / "IR" / "config.json"

        return Path.home() / "AppData" / "Roaming" / "IR" / "config.json"

    return Path("~/.config/argo/config.json").expanduser()


def load_config(
    path: str | Path | None = None,
) -> dict:
    config_path = default_config_path() if path is None else Path(path).expanduser()

    data = json.loads(
        config_path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "IR config root must be a JSON object.",
        )

    return _expand(data)
