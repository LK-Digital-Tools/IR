from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock

from argo.media import Result
from argo.voice_runtime import (
    VOSK_PHRASES,
    command_from_vosk_text,
    dispatch,
    get_vosk_model_path,
)


class VoiceRuntimeTests(unittest.TestCase):
    def test_public_surface_is_exactly_eleven_phrases(
        self,
    ):
        self.assertEqual(
            set(VOSK_PHRASES),
            {
                "ир плей",
                "ир пауза",
                "ир следующий",
                "ир предыдущий",
                "ир трек",
                "ир повтор",
                "ир тише",
                "ир громче",
                "ир стоп",
                "ир музыка",
                "ир удалить",
            },
        )

    def test_exact_phrases_map_to_expected_actions(
        self,
    ):
        self.assertEqual(
            VOSK_PHRASES,
            {
                "ир плей": "play",
                "ир пауза": "pause",
                "ир следующий": "next",
                "ир предыдущий": "previous",
                "ир трек": "status",
                "ир повтор": "repeat_current",
                "ир тише": "quieter",
                "ир громче": "louder",
                "ир стоп": "stop",
                "ир музыка": "open_player",
                "ир удалить": "delete_current",
            },
        )

    def test_spacing_and_case_are_normalized(
        self,
    ):
        self.assertEqual(
            command_from_vosk_text("  ИР   ПЛЕЙ  "),
            "play",
        )

    def test_english_phrases_can_be_selected(
        self,
    ):
        from argo.languages.en import COMMAND_PHRASES as EN_COMMAND_PHRASES

        self.assertEqual(
            command_from_vosk_text(
                "  IR   PLAY  ",
                EN_COMMAND_PHRASES,
            ),
            "play",
        )

    def test_commands_without_wake_word_are_rejected(
        self,
    ):
        for text in (
            "плей",
            "пауза",
            "следующий",
            "что играет",
            "стоп",
        ):
            with self.subTest(text=text):
                self.assertIsNone(command_from_vosk_text(text))

    def test_retired_aliases_are_rejected(
        self,
    ):
        for text in (
            "ирина плей",
            "эй ир плей",
            "ир плай",
            "ир мина",
            "ир что играет",
        ):
            with self.subTest(text=text):
                self.assertIsNone(command_from_vosk_text(text))

    def test_dispatch_calls_only_selected_handler(
        self,
    ):
        music = Mock()

        music.play.return_value = Result(
            True,
            "ok",
        )
        music.pause.return_value = Result(
            True,
            "ok",
        )
        music.next.return_value = Result(
            True,
            "ok",
        )
        music.previous.return_value = Result(
            True,
            "ok",
        )
        music.status.return_value = Result(
            True,
            "ok",
        )
        music.stop.return_value = Result(
            True,
            "ok",
        )
        music.open_player.return_value = Result(
            True,
            "ok",
        )

        result = dispatch(
            "next",
            music,
        )

        self.assertTrue(result.ok)

        music.next.assert_called_once_with()
        music.play.assert_not_called()
        music.pause.assert_not_called()
        music.previous.assert_not_called()
        music.status.assert_not_called()
        music.stop.assert_not_called()
        music.open_player.assert_not_called()

    def test_unknown_dispatch_action_fails_closed(
        self,
    ):
        music = Mock()

        result = dispatch(
            "minerva",
            music,
        )

        self.assertFalse(result.ok)

        self.assertIn(
            "Неизвестная команда",
            result.message,
        )


if __name__ == "__main__":
    unittest.main()


class VoiceModelConfigTests(unittest.TestCase):
    def test_selects_russian_model(self):
        path = get_vosk_model_path(
            {
                "models": {
                    "ru": "~/models/ru",
                    "en": "~/models/en",
                }
            },
            "ru",
        )

        self.assertTrue(
            str(path).endswith(str(Path("models") / "ru")),
        )

    def test_selects_english_model(self):
        path = get_vosk_model_path(
            {
                "models": {
                    "ru": "~/models/ru",
                    "en": "~/models/en",
                }
            },
            "en",
        )

        self.assertTrue(
            str(path).endswith(str(Path("models") / "en")),
        )

    def test_rejects_missing_language_model(self):
        with self.assertRaises(ValueError):
            get_vosk_model_path(
                {
                    "models": {
                        "ru": "~/models/ru",
                    }
                },
                "en",
            )

    def test_rejects_non_object_models(self):
        with self.assertRaises(ValueError):
            get_vosk_model_path(
                {
                    "models": ["bad"],
                },
                "ru",
            )


class PlatformCommandSurfaceTests(unittest.TestCase):
    def test_windows_language_surface_can_exclude_delete(self):
        from argo.languages.en import COMMAND_PHRASES as EN_COMMAND_PHRASES
        from argo.media import get_supported_actions

        supported = get_supported_actions(
            platform="win32",
        )
        phrases = {
            phrase: action for phrase, action in EN_COMMAND_PHRASES.items() if action in supported
        }

        self.assertEqual(
            len(phrases),
            10,
        )
        self.assertNotIn(
            "ir delete",
            phrases,
        )
