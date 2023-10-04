import requests


class Firefish:

    bearer_token: str = None
    api_base_url: str = None
    client_name = None

    @staticmethod
    def create_app(client_name: str, api_base_url: str, to_file: str):
        '''
        Do we even need to register the app?
        Not really, but this approach help us to define the API url and
            have it stored in a file.

        So we emulate the behaviour in Mastodon.py:
            - Create / Overwrite a file.
            - Write the client_name
            - Write the api_base_url
        '''

        if client_name is None or \
           api_base_url is None or \
           to_file is None:
            raise RuntimeError("All params are mandatory")

        # Clean the given API base URL before keeping it in mem.
        if api_base_url[-1] == "/":
            api_base_url = api_base_url[:-1]

        # Write both. Order is important.
        with open(to_file, 'w') as file:
            file.write(api_base_url + "\n")
            file.write(client_name)

    def __init__(
        self,
        client_id: str = None,
        api_base_url: str = None,
        access_token: str = None,
        feature_set: str = None
    ):
        '''
        If client_id comes we expect to find a file called like client_id
            which contains the api_base_url.
        If access_token comes we expect to find a file called like access_token
            which contains both api_base_url and the user token from login.
        If api_base_url comes we just take it.
        We just ignore feature_set.

        This is just to emulate the 2 step init that we have with Mastodon.py
        '''

        # So we received a client_id,
        # this is actually a filename so read it and get the params.
        if client_id is not None:
            with open(client_id, 'r') as file:
                self.api_base_url = file.readline().strip()
                self.client_name = file.readline().strip()

        # So we received an access_token,
        # this is actually a filename so read it and get the params.
        if access_token is not None:
            with open(access_token, 'r') as file:
                self.api_base_url = file.readline().strip()
                self.client_name = file.readline().strip()
                self.bearer_token = file.readline().strip()

        if api_base_url is not None:
            self.api_base_url = api_base_url

        # If we don't have a client_name, means that nothing came with. Error!
        if self.client_name is None and self.api_base_url is None:
            raise RuntimeError(
                "Mandatory params not found. Did you specify client_id or access_token?"
            )

    def log_in(self, username: str = None, password: str = None, to_file: str = None):
        '''
        I only need a Bearer token for authentication. Let's use "password" to receive it.
        If the method is called, I assume that the class instatiaton was using the client_id,
            so we should have already the client_id params in memory.
        If the to_file param is filled, we want to save the authentication into a file.
        '''
        if password is None:
            raise RuntimeError(
                "I need a Bearer token set into the 'password' param." +
                "Generate it and give it to me!"
            )

        self.bearer_token = password

        if to_file is not None:
            with open(to_file, 'w') as file:
                file.write(self.api_base_url + "\n")
                file.write(self.client_name + "\n")
                file.write(self.bearer_token)

    def __post_call(self, endpoint: str, headers: dict = {}, json_data: str = None):
        '''
        This is the method that proxies (and builds) all API POST calls.
        '''
        response = requests.post(
            url=f"{self.api_base_url}/{endpoint}",
            headers={
                **headers, **{
                    'Authorization': 'Bearer ' + self.bearer_token,
                }
            },
            json=json_data
        )

        if response.status_code == 200:
            return response.content
        else:
            raise RuntimeError(
                f"API Request ERROR -> {response.status_code}: {response.reason}"
            )

    def status_post(
        self,
        status: str,
        in_reply_to_id=None,
        media_ids=None,
        sensitive=False,
        visibility=None,
        spoiler_text=None,
        language=None,
        idempotency_key=None,
        content_type=None,
        scheduled_at=None,
        poll=None,
        quote_id=None
    ):
        '''
        Post a status. Can optionally be in reply to
            another status and contain media.

        media_ids should be a list. (If it’s not, the function
            will turn it into one.) It can contain up to four
            pieces of media (uploaded via media_post()).
            media_ids can also be the `media dicts`_
            returned by media_post() - they are unpacked
            automatically.

        [to implement] The sensitive boolean decides whether
            or not media attached to the post should be marked
            as sensitive, which hides it by default on the
            Mastodon web front-end.

        The visibility parameter is a string value and
            accepts any of: ‘direct’ - post will be visible
            only to mentioned users ‘private’ - post will be
            visible only to followers ‘unlisted’ - post will be
            public but not appear on the public timeline
            ‘public’ - post will be public

        If not passed in, visibility defaults to match the
            current account’s default-privacy setting
            (starting with Mastodon version 1.6) or its locked
            setting - private if the account is locked,
            public otherwise (for Mastodon versions lower than 1.6).

        [to implement] The spoiler_text parameter is a string to be
            shown as a warning before the text of the status.
            If no text is passed in, no warning will be displayed.

        Specify language to override automatic language detection.
            The parameter accepts all valid ISO 639-1 (2-letter)
            or for languages where that do not have one,
            639-3 (three letter) language codes.

        [to implement] You can set idempotency_key to a value to
            uniquely identify an attempt at posting a status.
            Even if you call this function more than once,
            if you call it with the same idempotency_key,
            only one status will be created.

        [to implement] Pass a datetime as scheduled_at to schedule
            the toot for a specific time (the time must be
            at least 5 minutes into the future). If this is passed,
            status_post returns a scheduled status dict instead.

        [to implement] Pass poll to attach a poll to the status.
            An appropriate object can be constructed using make_poll().
            Note that as of Mastodon version 2.8.2, you can only
            have either media or a poll attached, not both at the same time.

        [to implement] Specific to “pleroma” feature set::
            Specify content_type to set the content type of your
            post on Pleroma. It accepts ‘text/plain’ (default),
            ‘text/markdown’, ‘text/html’ and ‘text/bbcode’.
            This parameter is not supported on Mastodon servers,
            but will be safely ignored if set.

        [to implement] Specific to “fedibird” feature set::
            The quote_id parameter is a non-standard extension
            that specifies the id of a quoted status.

        [to implement] Returns a status dict with the new status.

        https://firefish.social/api-doc#operation/notes/create
        '''
        ENDPOINT = "api/notes/create"

        if status is None:
            raise RuntimeError("Field 'status' is mandatory")

        # Text is mandatory
        json_data = {
            "text": status,
        }

        # Do we have files?
        if media_ids is not None:
            json_data["fileIds"] = media_ids

        # Do we control visibility?
        if visibility is not None:
            # Translate the values from Mastodon to Firefish
            firefish_values_by_mastodon = {
                "public": "public",  # "": "home",
                "private": "followers",
                "direct": "specified",
                "unlisted": "hidden"
            }
            json_data["visibility"] = firefish_values_by_mastodon[visibility]

        # Do we define the language?
        if language is not None:
            json_data["lang"] = language

        # Is this a reply to another status?
        if in_reply_to_id is not None:
            json_data["replyId"] = in_reply_to_id

        # Make the call
        return self.__post_call(endpoint=ENDPOINT, json_data=json_data)
