from pyxavi import Media
from unittest.mock import Mock, patch
import os
import pytest
import requests
import tempfile

FIXTURES = [
    ["<a><p src=\"image_1.png\">whatever</p>", None, None],
    [
        "<b><img src=\"image_1.png\" /></b>", [{
            "src": "image_1.png"
        }], [{
            "url": "image_1.png", "alt_text": None
        }]
    ],
    [
        "<b><img src=\"image_1.png\" /><img src=\"image_2.png\" alt=\"Test\" /></b>",
        [{
            "src": "image_1.png"
        }, {
            "src": "image_2.png", "alt": "Test"
        }],
        [{
            "url": "image_1.png", "alt_text": None
        }, {
            "url": "image_2.png", "alt_text": "Test"
        }]
    ]
]


def test_parser_detects_img_tag():
    for fixture in FIXTURES:

        assert fixture[2] == Media().get_image_url_from_text(fixture[0])


def test_img_without_src_is_skipped():
    assert Media().get_image_url_from_text('<img alt="x"><img src="a.png">') == [
        {
            "url": "a.png", "alt_text": None
        }
    ]
    assert Media().get_image_url_from_text('<img alt="x">') is None


class _FakeDownload:

    def __init__(self, blocks, ok=True, fail_at=None):
        self.ok = ok
        self._blocks = blocks
        self._fail_at = fail_at

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def iter_content(self, size):
        for index, block in enumerate(self._blocks):
            if index == self._fail_at:
                raise requests.exceptions.ChunkedEncodingError("cut")
            yield block


def test_download_into_an_absolute_path():
    with tempfile.TemporaryDirectory() as folder:
        mocked_get = Mock(return_value=_FakeDownload([b"ab", b"cd"]))
        with patch.object(requests, "get", new=mocked_get):
            result = Media().download_from_url("https://x.com/a/pic.png", folder + "/")

        assert result == {"file": os.path.join(folder, "pic.png"), "mime_type": "image/png"}
        with open(result["file"], "rb") as stream:
            assert stream.read() == b"abcd"
        assert mocked_get.call_args.kwargs["timeout"] == 30


def test_failed_download_leaves_no_empty_file():
    with tempfile.TemporaryDirectory() as folder:
        with patch.object(requests, "get", new=Mock(return_value=_FakeDownload([], ok=False))):
            with pytest.raises(RuntimeError):
                Media().download_from_url("https://x.com/pic.png", folder)

        assert os.listdir(folder) == []


def test_download_cut_midway_leaves_no_partial_file():
    with tempfile.TemporaryDirectory() as folder:
        download = _FakeDownload([b"ab", b"cd"], fail_at=1)
        with patch.object(requests, "get", new=Mock(return_value=download)):
            with pytest.raises(requests.exceptions.ChunkedEncodingError):
                Media().download_from_url("https://x.com/pic.png", folder)

        assert os.listdir(folder) == []
