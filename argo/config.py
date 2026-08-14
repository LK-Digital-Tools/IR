from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = Path.home() / ".config" / "argo" / "config.json"


def _expand(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("~"):
        return str(Path(value).expanduser())
    if isinstance(value, list):
        return [_expand(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand(item) for key, item in value.items()}
    return value


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path).expanduser() if path else DEFAULT_CONFIG

    if not config_path.is_file():
        raise FileNotFoundError(f"IR config not found: {config_path}")

    data = json.loads(config_path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("IR config root must be a JSON object")

    return _expand(data)
