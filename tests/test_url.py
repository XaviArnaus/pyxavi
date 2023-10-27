from pyxavi.url import Url
import pytest


@pytest.mark.parametrize(
    argnames=('url', "params", 'expected_result'),
    argvalues=[
        (
            "http://domain.com/a/path.html?query=string#anchor",
            None,
            "http://domain.com/a/path.html?query=string#anchor"
        ),
        (
            "http://domain.com/a/path.html?query=string#anchor", {
                "scheme": True
            },
            "//domain.com/a/path.html?query=string#anchor"
        ),
        (
            "http://domain.com/a/path.html?query=string#anchor", {
                "netloc": True
            },
            "http://domain.com/a/path.html?query=string#anchor"
        ),
        (
            "http://domain.com/a/path.html?query=string#anchor", {
                "path": True
            },
            "http://domain.com?query=string#anchor"
        ),
        (
            "http://domain.com/a/path.html?query=string#anchor", {
                "query": True
            },
            "http://domain.com/a/path.html#anchor"
        ),
        (
            "http://domain.com/a/path.html?query=string#anchor", {
                "fragment": True
            },
            "http://domain.com/a/path.html?query=string"
        ),
        (
            "http://domain.com/a/path.html?query=string#anchor", {
                "scheme": True, "path": True, "query": True, "fragment": True
            },
            "//domain.com"
        ),
    ],
)
def test_clean(url, params, expected_result):
    assert Url.clean(url=url, remove_components=params) == expected_result
