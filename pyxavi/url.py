from urllib.parse import urlparse


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
