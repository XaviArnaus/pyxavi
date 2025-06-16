from pyxavi import Url
from unittest.mock import patch, Mock
import pytest
import requests
import feedparser


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


@pytest.mark.parametrize(
    argnames=('url', 'expected_result'),
    argvalues=[
        ("http://domain.com/a/path.html?query=string#anchor", True),
        ("http://example.com", True),
        ("https://example.com", True),
        ("https://www.example.com", True),
        ("https://www,example.com", False),
        ("https://www.example,com", False),
    ],
)
def test_is_valid(url, expected_result):
    assert Url.is_valid(url=url) == expected_result


@pytest.fixture
def base_url():
    return "https://example.com"


@pytest.fixture
def rss_url():
    return "/feed.rss"


@pytest.fixture
def atom_url():
    return "/feed.atom"


@pytest.fixture
def link_rss_absolute(base_url, rss_url):
    return f"<link rel=\"alternate\" type=\"application/rss+xml\" href=\"{base_url}{rss_url}\">"


@pytest.fixture
def link_atom_absolute(base_url, atom_url):
    return f"<link rel=\"alternate\" type=\"application/atom+xml\" href=\"{base_url}{atom_url}\">"  # noqa: E501


@pytest.fixture
def link_rss_relative(rss_url):
    return f"<link rel=\"alternate\" type=\"application/rss+xml\" href=\"{rss_url}\">"


@pytest.fixture
def link_atom_relative(atom_url):
    return f"<link rel=\"alternate\" type=\"application/atom+xml\" href=\"{atom_url}\">"


@pytest.fixture
def ahref_rss_absolute(base_url, rss_url):
    return f"<a href=\"{base_url}{rss_url}\"><i class=\"fa\"></i> RSS</a>"


@pytest.fixture
def ahref_atom_absolute(base_url, atom_url):
    return f"<a href=\"{base_url}{atom_url}\"><i class=\"fa\"></i> Atom</a>"


@pytest.fixture
def ahref_rss_relative(rss_url):
    return f"<a href=\"{rss_url}\"><i class=\"fa\"></i> RSS</a>"


@pytest.fixture
def ahref_atom_relative(atom_url):
    return f"<a href=\"{atom_url}h\"><i class=\"fa\"></i> Atom</a>"


@pytest.fixture
def content_placeholder():
    return """
<html lang="en">
  <head>
    <title>I am a title</title>
    <link rel="stylesheet" href="whatever.css" media="all" />
    %LINK%
  </head>
  <body>
    <h1>I am a title</h1>
    <div class="btn-group">
        %AHREF%
    </div>
  </body>
</html>
"""


@pytest.fixture
def content_with_no_link_alternate_nor_a_href(content_placeholder: str):
    return content_placeholder.replace("%LINK%", "").replace("%AHREF%", "")


@pytest.fixture
def content_with_link_alternate_but_not_a_href_absolute(
    content_placeholder: str, link_rss_absolute
):
    return content_placeholder.replace("%LINK%", link_rss_absolute).replace("%AHREF%", "")


@pytest.fixture
def content_with_no_link_alternate_but_a_href_absolute(
    content_placeholder: str, ahref_rss_absolute
):
    return content_placeholder.replace("%LINK%", "").replace("%AHREF%", ahref_rss_absolute)


@pytest.fixture
def content_with_both_link_alternate_and_a_href_absolute(
    content_placeholder: str, link_rss_absolute, ahref_rss_absolute
):
    return content_placeholder.replace("%LINK%", link_rss_absolute
                                       ).replace("%AHREF%", ahref_rss_absolute)


@pytest.fixture
def content_with_link_alternate_but_not_a_href_relative(
    content_placeholder: str, link_rss_relative
):
    return content_placeholder.replace("%LINK%", link_rss_relative).replace("%AHREF%", "")


@pytest.fixture
def content_with_no_link_alternate_but_a_href_relative(
    content_placeholder: str, ahref_rss_relative
):
    return content_placeholder.replace("%LINK%", "").replace("%AHREF%", ahref_rss_relative)


@pytest.fixture
def content_with_both_link_alternate_and_a_href_relative(
    content_placeholder: str, link_rss_relative, ahref_rss_relative
):
    return content_placeholder.replace("%LINK%", link_rss_relative
                                       ).replace("%AHREF%", ahref_rss_relative)


@pytest.fixture
def content_with_atom_and_rss_in_links(
    content_placeholder: str, link_rss_absolute, link_atom_relative
):
    links = link_atom_relative + "\n" + link_rss_absolute
    return content_placeholder.replace("%LINK%", links).replace("%AHREF%", "")


@pytest.fixture
def content_with_rss_and_atom_in_links(
    content_placeholder: str, link_rss_absolute, link_atom_relative
):
    links = link_rss_absolute + "\n" + link_atom_relative
    return content_placeholder.replace("%LINK%", links).replace("%AHREF%", "")


@pytest.fixture
def case_maho_dev():
    return """
<html lang="en-us">
  <head>
    <title>Raccoon Bits</title>
    <link rel="alternate" type="application/rss+xml" href="https://maho.dev/index.xml" title="Raccoon Bits">
  </head>
  <body>
    <h1>I am a title</h1>
    <div class="btn-group">
        <h2>hello</2>
    </div>
  </body>
</html>
"""  # noqa: E501


@pytest.fixture
def case_garrigos_cat():
    return """
<html lang="en-us">
  <head>
    <title>Garrigos.cat |</title>
  </head>
  <body>
    <div class="col-sm text-center pt-1">
        <a href="https://github.com/robertgarrigos" class="pr-3"><i class="fab fa-github-square fa-2x"></i></a>
        <a href="https://www.garrigos.cat/rss.xml" class="pr-3"><i class="fas fa-rss-square fa-2x"></i></a>
        <a href="https://mastodont.cat/@robertgarrigos" rel="me" class="pr-3"><i class="fab fa-mastodon fa-2x"></i></a>
    </div>
  </body>
</html>
"""  # noqa: E501


@pytest.fixture
def case_retiolus_net():
    return """
<html lang="en-us">
  <head>
    <title>Posts · retiolus</title>
    <link rel="alternate" type="application/rss+xml" href="/posts/index.xml" title="retiolus" />
  </head>
  <body>
   <h1>I am a title</h1>
    <div class="btn-group">
        <h2>hello</2>
    </div>
  </body>
</html>
"""  # noqa: E501


@pytest.fixture
def case_world_hey_com():
    return """
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>David Heinemeier Hansson</title>
    <link rel="alternate" type="application/atom+xml" title="Feed" href="https://world.hey.com/dhh/feed.atom">
  </head>
  <body>
   <h1>I am a title</h1>
    <div class="btn-group">
        <h2>hello</2>
    </div>
  </body>
</html>
"""  # noqa: E501


@pytest.fixture
def case_xavier_arnaus_net():
    return """
<html lang="en">
    <head>
        <title>Home | Xavier.Arnaus.net</title>
        <link rel="alternate" type="application/atom+xml" title="Xavi's blog" href="https://xavier.arnaus.net/blog.atom" />
        <link rel="alternate" type="application/rss+xml" title="Xavi's blog" href="https://xavier.arnaus.net/blog.rss" />
  </head>
  <body>
   <h1>I am a title</h1>
       <div class="btn-group">
        <a class="btn btn-warning" href="/blog.atom"><i class="fa fa-rss-square"></i> Atom 1.0</a>
        <a class="btn btn-warning" href="/blog.rss"><i class="fa fa-rss-square"></i> RSS</a>
    </div>
    <div class="btn-group">
        <a class="btn btn-warning" href="/blog.atom/tag:english"><i class="fa fa-rss-square"></i> Atom 1.0</a>
        <a class="btn btn-warning" href="/blog.rss/tag:english"><i class="fa fa-rss-square"></i> RSS</a>
    </div>
    <div class="btn-group">
        <a class="btn btn-warning" href="/blog.atom/tag:català"><i class="fa fa-rss-square"></i> Atom 1.0</a>
        <a class="btn btn-warning" href="/blog.rss/tag:català"><i class="fa fa-rss-square"></i> RSS</a>
    </div>
  </body>
</html>
"""  # noqa: E501


@pytest.fixture
def rss_feed():
    feed = """
<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title>Xavier Arnaus&#039; Blog</title>
        <link>https://xavier.arnaus.net/blog</link>
        <atom:link href="https://xavier.arnaus.net/blog.rss/tag:english" rel="self" type="application/rss+xml"/>
        <description>Feed from my Blog</description>
        <language>en</language>
        <lastBuildDate>Wed, 14 Feb 2024 22:30:03 +0100</lastBuildDate>
        <item>
            <title>Migrate the firefish admin account to another instance</title>
            <link>https://xavier.arnaus.net/blog/migrate-the-firefish-admin-account-to-another-instance</link>
            <guid>https://xavier.arnaus.net/blog/migrate-the-firefish-admin-account-to-another-instance</guid>
            <pubDate>Mon, 05 Feb 2024 16:30:04 +0100</pubDate>
            <description>
                <![CDATA[
                    <img alt="" src="https://xavier.arnaus.net/user/pages/02.blog/51.migrate-the-firefish-admin-account-to-another-instance/mastodon_migration.jpeg" />
                    <p>In a <a href="/blog/install-mastodon-glitch-edition-on-a-raspberry-pi-4">previous article</a> I installed a #Mastodon #Glitch Edition intended to become my techie instance, moving there my bots from the previous #Firefish instance. The final step was to migrate my personal nerd account and this article was supposed to be a walk through… just that it’s not. It is a log about my adventure and failures to move an <em>admin</em> account away from Firefish, to execute a successful #fediverse account #migration against all odds.</p>
                    <p>So bear with me, grab a sit and a drink, and let me explain you how (not) to do a migration between fediverse instances.</p>
                    ]]>
            </description>
            <category>english</category>
        </item>
        <item>
            <title>Update Mastodon to v4.2.5 and keeping customisations</title>
            <link>https://xavier.arnaus.net/blog/update-mastodon-to-v4-2-5-and-keeping-customisations</link>
            <guid>https://xavier.arnaus.net/blog/update-mastodon-to-v4-2-5-and-keeping-customisations</guid>
            <pubDate>Wed, 14 Feb 2024 22:30:03 +0100</pubDate>
            <description>
                <![CDATA[
                    <img alt="" src="https://xavier.arnaus.net/user/pages/02.blog/50.update-mastodon-to-v4-2-5-and-keeping-customisations/Mastodon 4.2.5.png" />
                    <p>Recently the new #Mastodon v4.2.5 was announced and with it the urge of a security fix. In a previous article I explained a strategy to keep the code customised and up to date, and even working with #git is part of my daily work, I feel like explaining in detail the process so that I will remember it for future references and also may help anybody that has the instance somewhat customised.</p>
                ]]>
            </description>
            <category>english</category>
        </item>
    </channel>
</rss>
"""  # noqa: E501
    return feedparser.parse(feed)


@pytest.fixture
def atom_feed():
    feed = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Xavier Arnaus&#039; Blog</title>
    <link href="https://xavier.arnaus.net/blog.atom/tag:english" rel="self" />
    <subtitle>Feed from my Blog</subtitle>
    <updated>2024-02-14T22:30:03+01:00</updated>
    <author>
        <name>Xavi</name>
    </author>
    <id>https://xavier.arnaus.net/blog</id>
    <entry>
        <title>Migrate the firefish admin account to another instance</title>
        <id>https://xavier.arnaus.net/blog/migrate-the-firefish-admin-account-to-another-instance</id>
        <updated>2024-02-05T16:30:04+01:00</updated>
        <published>2024-02-05T16:30:04+01:00</published>
        <link href="https://xavier.arnaus.net/blog/migrate-the-firefish-admin-account-to-another-instance"/>
        <category term="english" />
            <![CDATA[
                <img alt="" src="https://xavier.arnaus.net/user/pages/02.blog/51.migrate-the-firefish-admin-account-to-another-instance/mastodon_migration.jpeg" />
                <p>In a <a href="/blog/install-mastodon-glitch-edition-on-a-raspberry-pi-4">previous article</a> I installed a #Mastodon #Glitch Edition intended to become my techie instance, moving there my bots from the previous #Firefish instance. The final step was to migrate my personal nerd account and this article was supposed to be a walk through… just that it’s not. It is a log about my adventure and failures to move an <em>admin</em> account away from Firefish, to execute a successful #fediverse account #migration against all odds.</p>
                <p>So bear with me, grab a sit and a drink, and let me explain you how (not) to do a migration between fediverse instances.</p>
            ]]>
        </content>
    </entry>
    <entry>
        <title>Update Mastodon to v4.2.5 and keeping customisations</title>
        <id>https://xavier.arnaus.net/blog/update-mastodon-to-v4-2-5-and-keeping-customisations</id>
        <updated>2024-02-14T22:30:03+01:00</updated>
        <published>2024-02-14T22:30:03+01:00</published>
        <link href="https://xavier.arnaus.net/blog/update-mastodon-to-v4-2-5-and-keeping-customisations"/>
        <category term="english" />
            <![CDATA[
                <img alt="" src="https://xavier.arnaus.net/user/pages/02.blog/50.update-mastodon-to-v4-2-5-and-keeping-customisations/Mastodon 4.2.5.png" />
                <p>Recently the new #Mastodon v4.2.5 was announced and with it the urge of a security fix. In a previous article I explained a strategy to keep the code customised and up to date, and even working with #git is part of my daily work, I feel like explaining in detail the process so that I will remember it for future references and also may help anybody that has the instance somewhat customised.</p>
            ]]>
        </content>
    </entry>
</feed>
"""   # noqa: E501
    return feedparser.parse(feed)


@pytest.mark.parametrize(
    argnames=('content_test', 'specific_base_url', 'expected_result_fixtures'),
    argvalues=[
        # Common cases
        ("content_with_no_link_alternate_nor_a_href", None, []),
        ("content_with_link_alternate_but_not_a_href_absolute", None, ["rss_url"]),
        ("content_with_no_link_alternate_but_a_href_absolute", None, ["rss_url"]),
        ("content_with_both_link_alternate_and_a_href_absolute", None, ["rss_url"]),
        ("content_with_link_alternate_but_not_a_href_relative", None, ["rss_url"]),
        ("content_with_no_link_alternate_but_a_href_relative", None, ["rss_url"]),
        ("content_with_both_link_alternate_and_a_href_relative", None, ["rss_url"]),
        # Testing the sorting.
        ("content_with_atom_and_rss_in_links", None, ["rss_url", "atom_url"]),
        ("content_with_rss_and_atom_in_links", None, ["rss_url", "atom_url"]),
        # Specific cases (failures saw online)
        ("case_maho_dev", None, ["https://maho.dev/index.xml"]),
        ("case_garrigos_cat", None, ["https://www.garrigos.cat/rss.xml"]),
        (
            "case_retiolus_net",
            "https://retiolus.net/", ["https://retiolus.net/posts/index.xml"]
        ),
        ("case_world_hey_com", None, ["https://world.hey.com/dhh/feed.atom"]),
        (
            "case_xavier_arnaus_net",
            "https://xavier.arnaus.net/blog",
            ['https://xavier.arnaus.net/blog.rss', 'https://xavier.arnaus.net/blog.atom']
        ),
    ],
)
def test_findfeeds(
    content_test,
    specific_base_url,
    expected_result_fixtures,
    base_url,
    rss_feed,
    atom_feed,
    request
):

    content_to_return = request.getfixturevalue(content_test)
    base_url = specific_base_url if specific_base_url else base_url
    url = base_url + "/fake_url.html"
    expected_result = []
    for fixture in expected_result_fixtures:
        if str(fixture).startswith("http"):
            expected_result.append(fixture)
        else:
            expected_result.append(base_url + request.getfixturevalue(fixture))

    class FakeRequest:
        url: str
        text: str

        def __init__(self, url, text) -> None:
            self.url = url
            self.text = text

    def mocked_feedparse(url):
        return rss_feed if "rss" in url else atom_feed

    mocked_requests_head = Mock()
    mocked_requests_head.return_value = FakeRequest(url=url, text="")
    mocked_requests_get = Mock()
    mocked_requests_get.return_value = FakeRequest(url=url, text=content_to_return)
    with patch.object(requests, "head", new=mocked_requests_head):
        with patch.object(requests, "get", new=mocked_requests_get):
            with patch.object(feedparser, "parse", new=mocked_feedparse):
                assert Url.findfeeds(url=url) == expected_result
