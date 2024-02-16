from urllib.parse import urlparse
import validators
import requests
import feedparser
from bs4 import BeautifulSoup as bs4
from pyxavi.debugger import dd

class Url:

    @staticmethod
    def clean(url, remove_components: dict = None) -> str:

        if remove_components is None:
            remove_components = {}

        to_remove = {
            "scheme": False,
            "netloc": False,
            "path": False,
            "params": False,
            "query": False,
            "fragment": False
        }
        to_remove = {**to_remove, **remove_components}

        parsed = urlparse(url)

        if to_remove["scheme"] is True:
            parsed = parsed._replace(scheme="")
        if to_remove["netloc"] is True:
            parsed._replace(netloc="")
        if to_remove["path"] is True:
            parsed = parsed._replace(path="")
        if to_remove["params"] is True:
            parsed = parsed._replace(params="")
        if to_remove["query"] is True:
            parsed = parsed._replace(query="")
        if to_remove["fragment"] is True:
            parsed = parsed._replace(fragment="")

        return parsed.geturl()

    @staticmethod
    def is_valid(url) -> bool:
        return True if validators.url(url) else False

    @staticmethod
    def findfeeds(url: str):
        """
        It returns a list of URLs found in the given site's URL that have entries.
        so be prepared to receive an array.
        """

        def by_priority(element):
            if "rss" in element:
                return 1
            elif "atom" in element:
                return 3
            else:
                return 5

        # kindly adapted from
        #   https://alexmiller.phd/posts/python-3-feedfinder-rss-detection-from-url/
        # What I added:
        #   1. Send a HEAD first, so we can follow redirections
        #   2. Do not search within the body, only the LINK inside the HEAD
        #   3. Add the base URL in case the RSS link is relative
        #   4. Sort, I want RSS mainly

        # Get the header first, so we know if there is a redirection
        r = requests.head(url, allow_redirects=True)

        # Now get the content from the real URL
        raw = requests.get(r.url).text
        result = []
        possible_feeds = []

        # Prepare the base URL, as sometimes the Feed comes relative
        parsed_url = urlparse(url)
        base = parsed_url.scheme+"://"+parsed_url.hostname

        # We'll parse the HTML using beautifulsoup
        html = bs4(raw, features="html.parser")

        # The "link" tags that are rel="alternate" may contain the feed
        feed_urls = html.findAll("link", rel="alternate")
        if len(feed_urls) >= 1:
            for f in feed_urls:
                # They have to have a "type" attribute
                t = f.get("type", None)
                print(t)
                if t:
                    # ... and it has to contain "rss" or "xml"
                    if "rss" in t or "xml" in t:
                        href = f.get("href", None)
                        if href:
                            possible_feeds.append(href)

        # Now search for "a" tags in the body
        atags = html.findAll("a")
        for a in atags:
            href = a.get("href",None)
            if href:
                # ... that contain "rss" or "xml" in the "href" attribute
                if "xml" in href or "rss" in href or "feed" in href:
                    possible_feeds.append(href)

        # Now loop through all possible feeds and check if they are valid.
        for possible_feed in list(set(possible_feeds)):

            # Is this URL relative? then add the base
            parsed_possible_feed = urlparse(possible_feed)
            if not parsed_possible_feed.scheme or not parsed_possible_feed.hostname:
                possible_feed = base + possible_feed

            # If it's a valid feed we add it into the resulting list
            if Url.is_a_valid_feed(possible_feed) and possible_feed not in result:
                result.append(possible_feed)

        # Finally, apply sorting, as RSS are more prio than Atom...
        sorted(result, key=by_priority)

        # Return the list found!
        return (result)
    
    @staticmethod
    def is_a_valid_feed(url) -> bool:
        f = feedparser.parse(url)
        return len(f.entries) > 0