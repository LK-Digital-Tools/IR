from __future__ import annotations

from .en import COMMAND_PHRASES as EN_COMMAND_PHRASES
from .ru import COMMAND_PHRASES as RU_COMMAND_PHRASES

LANGUAGE_PACKS = {
    "ru": RU_COMMAND_PHRASES,
    "en": EN_COMMAND_PHRASES,
}


def get_command_phrases(
    language: str,
) -> dict[str, str]:
    key = language.strip().casefold()

    try:
        return LANGUAGE_PACKS[key]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported IR language: {language}",
        ) from exc
