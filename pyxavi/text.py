import re

# The regular expression is expensive to build (it has thousands of alternatives),
#   so it is built once, the first time that it is needed.
_EMOJI_REGEXP = None


class Text:

    @staticmethod
    def remove_emojis(text: str) -> str:
        return Text._get_emoji_regexp().sub(r'', text)

    @staticmethod
    def _get_emoji_regexp():
        global _EMOJI_REGEXP
        if _EMOJI_REGEXP is None:
            # Imported here: it is a heavy import that is only needed in this case.
            import emoji

            # Sort emoji by length to make sure multi-character emojis are
            # matched first
            emojis = sorted(emoji.EMOJI_DATA, key=len, reverse=True)
            pattern = '(' + '|'.join(re.escape(u) for u in emojis) + ')'
            _EMOJI_REGEXP = re.compile(pattern)
        return _EMOJI_REGEXP
