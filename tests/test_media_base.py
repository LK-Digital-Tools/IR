from __future__ import annotations

import unittest

from argo.media import Result
from argo.media.base import Result as BaseResult


class MediaBaseTests(unittest.TestCase):
    def test_result_is_platform_neutral(self):
        result = Result(
            True,
            "ok",
        )

        self.assertIs(Result, BaseResult)
        self.assertTrue(result.ok)
        self.assertEqual(result.message, "ok")
