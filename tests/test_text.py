from pyxavi import Text
from unittest.mock import patch
import pyxavi.text


def test_remove_emojis():
    assert Text.remove_emojis("hi \U0001F600 there \U0001F44D!") == "hi  there !"


def test_remove_emojis_also_from_an_instance():
    assert Text().remove_emojis("a\U0001F600b") == "ab"


def test_the_emoji_regexp_is_built_only_once():
    with patch.object(pyxavi.text, "_EMOJI_REGEXP", new=None):
        first = Text._get_emoji_regexp()
        second = Text._get_emoji_regexp()

    assert first is second
