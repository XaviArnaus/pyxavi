from pyxavi.firefish import Firefish
from unittest.mock import Mock, patch, mock_open, call, MagicMock
from unittest import TestCase
import pytest
import builtins
import requests


@pytest.mark.parametrize(
    argnames=('client_name', 'api_base_url', 'to_file', 'expected_values'),
    argvalues=[
        (None, None, None, False), ("Client", "https://social.devnamic.com", None, False),
        ("Client", None, "client.secret", False),
        (None, "https://social.devnamic.com", "client.secret", False),
        (
            "Client",
            "https://social.devnamic.com",
            "client.secret", ("Client", "https://social.devnamic.com")
        ),
        (
            "Client",
            "https://social.devnamic.com/",
            "client.secret", ("Client", "https://social.devnamic.com")
        )
    ],
)
def test_create_app(client_name, api_base_url, to_file, expected_values):

    if expected_values is False:
        with TestCase.assertRaises("pyxavi.firefish", RuntimeError):
            Firefish.create_app(
                client_name=client_name, api_base_url=api_base_url, to_file=to_file
            )
    else:
        expected_client_name, expected_api_base_url = expected_values
        mocked_open_file = MagicMock()
        with patch.object(builtins, "open", mock_open(mock=mocked_open_file)):
            Firefish.create_app(
                client_name=client_name, api_base_url=api_base_url, to_file=to_file
            )

            handle = mocked_open_file()
            handle.write.assert_has_calls(
                [call(expected_api_base_url + "\n"), call(expected_client_name)]
            )


def test_init_empty_fails():
    with TestCase.assertRaises("pyxavi.firefish", RuntimeError):
        _ = Firefish()


def test_init_with_client_id():
    client_id_filename = "client.secret"
    client_id_client_name = "Client"
    client_id_api_base_url = "https://social.devnamic.com"
    client_id_content = "\n".join([client_id_api_base_url, client_id_client_name])

    mocked_open_file = MagicMock()
    with patch.object(builtins,
                      "open",
                      mock_open(mock=mocked_open_file, read_data=client_id_content)):
        instance = Firefish(client_id=client_id_filename)

        mocked_open_file.assert_called_once_with(client_id_filename, "r")
        assert instance.api_base_url == client_id_api_base_url
        assert instance.client_name == client_id_client_name


def test_init_with_client_id_and_api_base_url():
    client_id_filename = "client.secret"
    client_id_client_name = "Client"
    client_id_api_base_url = "https://social.devnamic.com"
    instance_api_base_url = "https://talamanca.social"
    client_id_content = "\n".join([client_id_api_base_url, client_id_client_name])

    mocked_open_file = MagicMock()
    with patch.object(builtins,
                      "open",
                      mock_open(mock=mocked_open_file, read_data=client_id_content)):
        instance = Firefish(client_id=client_id_filename, api_base_url=instance_api_base_url)

        mocked_open_file.assert_called_once_with(client_id_filename, "r")
        assert instance.api_base_url == instance_api_base_url
        assert instance.client_name == client_id_client_name


def test_init_with_access_token():
    access_token_filename = "user.secret"
    access_token_client_name = "Client"
    access_token_api_base_url = "https://social.devnamic.com"
    access_token_token = "abcdefg123456"
    access_token_content = "\n".join(
        [access_token_api_base_url, access_token_client_name, access_token_token]
    )

    mocked_open_file = MagicMock()
    with patch.object(builtins,
                      "open",
                      mock_open(mock=mocked_open_file, read_data=access_token_content)):
        instance = Firefish(access_token=access_token_filename)

        mocked_open_file.assert_called_once_with(access_token_filename, "r")
        assert instance.api_base_url == access_token_api_base_url
        assert instance.client_name == access_token_client_name
        assert instance.bearer_token == access_token_token


def test_init_with_access_token_with_api_base_url():
    access_token_filename = "user.secret"
    access_token_client_name = "Client"
    access_token_api_base_url = "https://social.devnamic.com"
    instance_api_base_url = "https://talamanca.social"
    access_token_token = "abcdefg123456"
    access_token_content = "\n".join(
        [access_token_api_base_url, access_token_client_name, access_token_token]
    )

    mocked_open_file = MagicMock()
    with patch.object(builtins,
                      "open",
                      mock_open(mock=mocked_open_file, read_data=access_token_content)):
        instance = Firefish(
            access_token=access_token_filename, api_base_url=instance_api_base_url
        )

        mocked_open_file.assert_called_once_with(access_token_filename, "r")
        assert instance.api_base_url == instance_api_base_url
        assert instance.client_name == access_token_client_name
        assert instance.bearer_token == access_token_token


def test_log_in_without_password():
    client_id_filename = "client.secret"
    client_id_client_name = "Client"
    client_id_api_base_url = "https://social.devnamic.com"
    client_id_content = "\n".join([client_id_api_base_url, client_id_client_name])

    mocked_open_file = MagicMock()
    with patch.object(builtins,
                      "open",
                      mock_open(mock=mocked_open_file, read_data=client_id_content)):
        instance = Firefish(client_id=client_id_filename)
        with TestCase.assertRaises(instance, RuntimeError):
            instance.log_in(username="test")


def test_log_in_with_password():
    client_id_filename = "client.secret"
    client_id_client_name = "Client"
    client_id_api_base_url = "https://social.devnamic.com"
    client_id_content = "\n".join([client_id_api_base_url, client_id_client_name])
    token = "abcdefg123456"
    access_token_filename = "user.secret"
    access_token_filename = "user.secret"
    access_token_client_name = "Client"
    access_token_api_base_url = "https://social.devnamic.com"

    with patch.object(builtins, "open", mock_open(read_data=client_id_content)):
        instance = Firefish(client_id=client_id_filename)

    mocked_open_file = MagicMock()
    with patch.object(builtins, "open", mock_open(mock=mocked_open_file)):
        instance.log_in(username="test", password=token, to_file=access_token_filename)

        handle = mocked_open_file()
        handle.write.assert_has_calls(
            [
                call(access_token_api_base_url + "\n"),
                call(access_token_client_name + "\n"),
                call(token)
            ]
        )

        assert instance.bearer_token == token


@pytest.mark.parametrize(
    argnames=(
        'endpoint',
        'headers',
        'json_data',
        'expected_status_code',
        'expected_content',
        'expected_reason'
    ),
    argvalues=[
        ("/api/notes/create", {}, {
            "text": "test"
        }, 200, "OK", None),
        ("/api/notes/create", {}, {
            "text": "test"
        }, 401, None, "Unauthortised")
    ],
)
def test__post_call(
    endpoint, headers, json_data, expected_status_code, expected_content, expected_reason
):
    access_token_filename = "user.secret"
    access_token_client_name = "Client"
    access_token_api_base_url = "https://social.devnamic.com"
    access_token_token = "abcdefg123456"
    access_token_content = "\n".join(
        [access_token_api_base_url, access_token_client_name, access_token_token]
    )

    with patch.object(builtins, "open", mock_open(read_data=access_token_content)):
        instance = Firefish(access_token=access_token_filename)

    class Response:
        status_code: int
        content: str
        reason: str

        def __init__(self, status_code: int, content: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.content = content
            self.reason = reason

    mocked_requests_post = Mock()
    mocked_requests_post.return_value = Response(
        status_code=expected_status_code, content=expected_content, reason=expected_reason
    )
    with patch.object(requests, "post", new=mocked_requests_post):
        if expected_status_code == 200:
            returned_content = instance._Firefish__post_call(
                endpoint=endpoint, headers=headers, json_data=json_data
            )
            assert returned_content == expected_content
        else:
            with TestCase.assertRaises(instance, RuntimeError):
                instance._Firefish__post_call(
                    endpoint=endpoint, headers=headers, json_data=json_data
                )


@pytest.mark.parametrize(
    argnames=(
        'status',
        'in_reply_to_id',
        'media_ids',
        'sensitive',
        'visibility',
        'spoiler_text',
        'language',
        'idempotency_key',
        'content_type',
        'scheduled_at',
        'poll',
        'quote_id',
        'expected_endpoint',
        'expected_json'
    ),
    argvalues=[
        (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
        (
            "test content",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "api/notes/create", {
                "text": "test content"
            }
        ),
        (
            "test content",
            None, [123],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "api/notes/create", {
                "text": "test content", "fileIds": [123]
            }
        ),
        (
            "test content",
            None,
            None,
            None,
            "public",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "api/notes/create", {
                "text": "test content", "visibility": "public"
            }
        ),
        (
            "test content",
            None,
            None,
            None,
            "private",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "api/notes/create", {
                "text": "test content", "visibility": "followers"
            }
        ),
        (
            "test content",
            None,
            None,
            None,
            "direct",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "api/notes/create", {
                "text": "test content", "visibility": "specified"
            }
        ),
        (
            "test content",
            None,
            None,
            None,
            "unlisted",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "api/notes/create", {
                "text": "test content", "visibility": "hidden"
            }
        ),
        (
            "test content",
            None,
            None,
            None,
            None,
            None,
            "ca",
            None,
            None,
            None,
            None,
            None,
            "api/notes/create", {
                "text": "test content", "lang": "ca"
            }
        ),
        (
            "test content",
            1234,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "api/notes/create", {
                "text": "test content", "replyId": 1234
            }
        ),
    ],
)
def test_status_post(
    status,
    in_reply_to_id,
    media_ids,
    sensitive,
    visibility,
    spoiler_text,
    language,
    idempotency_key,
    content_type,
    scheduled_at,
    poll,
    quote_id,
    expected_endpoint,
    expected_json
):

    access_token_filename = "user.secret"
    access_token_client_name = "Client"
    access_token_api_base_url = "https://social.devnamic.com"
    access_token_token = "abcdefg123456"
    access_token_content = "\n".join(
        [access_token_api_base_url, access_token_client_name, access_token_token]
    )

    with patch.object(builtins, "open", mock_open(read_data=access_token_content)):
        instance = Firefish(access_token=access_token_filename)

    if status is None:
        with TestCase.assertRaises(instance, RuntimeError):
            instance.status_post(
                status,
                in_reply_to_id,
                media_ids,
                sensitive,
                visibility,
                spoiler_text,
                language,
                idempotency_key,
                content_type,
                scheduled_at,
                poll,
                quote_id
            )
    else:
        mocked_post_call = Mock()
        with patch.object(instance, "_Firefish__post_call", new=mocked_post_call):
            _ = instance.status_post(
                status,
                in_reply_to_id,
                media_ids,
                sensitive,
                visibility,
                spoiler_text,
                language,
                idempotency_key,
                content_type,
                scheduled_at,
                poll,
                quote_id
            )

            mocked_post_call.assert_called_once_with(
                endpoint=expected_endpoint, json_data=expected_json
            )