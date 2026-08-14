from __future__ import annotations

import unittest

from argo.languages.en import COMMAND_PHRASES as EN_COMMAND_PHRASES
from argo.languages.ru import COMMAND_PHRASES as RU_COMMAND_PHRASES


class LanguagePackTests(unittest.TestCase):
    def test_ru_and_en_have_same_action_surface(self):
        self.assertEqual(
            set(RU_COMMAND_PHRASES.values()),
            set(EN_COMMAND_PHRASES.values()),
        )

    def test_each_language_has_exactly_eleven_phrases(self):
        self.assertEqual(len(RU_COMMAND_PHRASES), 11)
        self.assertEqual(len(EN_COMMAND_PHRASES), 11)

    def test_english_pack_maps_expected_commands(self):
        self.assertEqual(EN_COMMAND_PHRASES["ir play"], "play")
        self.assertEqual(EN_COMMAND_PHRASES["ir music"], "open_player")
        self.assertEqual(EN_COMMAND_PHRASES["ir delete"], "delete_current")


class LanguageSelectionTests(unittest.TestCase):
    def test_language_loader_returns_russian_pack(self):
        from argo.languages import get_command_phrases

        self.assertIs(
            get_command_phrases("ru"),
            RU_COMMAND_PHRASES,
        )

    def test_language_loader_returns_english_pack(self):
        from argo.languages import get_command_phrases

        self.assertIs(
            get_command_phrases("EN"),
            EN_COMMAND_PHRASES,
        )

    def test_language_loader_rejects_unknown_language(self):
        from argo.languages import get_command_phrases

        with self.assertRaises(ValueError):
            get_command_phrases("de")
