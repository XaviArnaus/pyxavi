from pyxavi.firefish import Firefish
from unittest.mock import Mock, patch, mock_open, call, MagicMock
from unittest import TestCase
import pytest
import builtins
import requests
import socket

@pytest.mark.parametrize(
    argnames=('client_name', 'api_base_url', 'to_file', 'expected_values'),
    argvalues=[
        (None, None, None, False),
        ("Client", "https://social.devnamic.com", None, False),
        ("Client", None, "client.secret", False),
        (None, "https://social.devnamic.com", "client.secret", False),
        ("Client", "https://social.devnamic.com", "client.secret", ("Client", "https://social.devnamic.com")),
        ("Client", "https://social.devnamic.com/", "client.secret", ("Client", "https://social.devnamic.com"))
    ],
)
def test_create_app(client_name, api_base_url, to_file, expected_values):

    if expected_values is False:
        with TestCase.assertRaises("pyxavi.firefish", RuntimeError):
            Firefish.create_app(client_name=client_name,
                            api_base_url=api_base_url,
                            to_file=to_file)
    else:
        expected_client_name, expected_api_base_url = expected_values
        mocked_open_file = MagicMock()
        with patch.object(builtins, "open", mock_open(mock=mocked_open_file)):
            Firefish.create_app(client_name=client_name,
                            api_base_url=api_base_url,
                            to_file=to_file)
            
            handle = mocked_open_file()
            handle.write.assert_has_calls(
                [
                    call(expected_api_base_url + "\n"),
                    call(expected_client_name)
                ]
            )

def test_init_empty_fails():
    with TestCase.assertRaises("pyxavi.firefish", RuntimeError):
        _ = Firefish()

def test_init_with_client_id():
    client_id_filename = "client.secret"
    client_id_client_name = "Client"
    client_id_api_base_url = "https://social.devnamic.com"
    client_id_content = f"{client_id_api_base_url}\n{client_id_client_name}"

    mocked_open_file = MagicMock()
    with patch.object(builtins, "open", mock_open(mock=mocked_open_file, read_data=client_id_content)):
        instance = Firefish(client_id=client_id_filename)

        mocked_open_file.assert_called_once_with(client_id_filename, "r")
        assert instance.api_base_url == client_id_api_base_url
        assert instance.client_name == client_id_client_name

def test_init_with_client_id_and_api_base_url():
    client_id_filename = "client.secret"
    client_id_client_name = "Client"
    client_id_api_base_url = "https://social.devnamic.com"
    instance_api_base_url = "https://talamanca.social"
    client_id_content = f"{client_id_api_base_url}\n{client_id_client_name}"

    mocked_open_file = MagicMock()
    with patch.object(builtins, "open", mock_open(mock=mocked_open_file, read_data=client_id_content)):
        instance = Firefish(client_id=client_id_filename, api_base_url=instance_api_base_url)

        mocked_open_file.assert_called_once_with(client_id_filename, "r")
        assert instance.api_base_url == instance_api_base_url
        assert instance.client_name == client_id_client_name


def test_init_with_access_token():
    access_token_filename = "user.secret"
    access_token_client_name = "Client"
    access_token_api_base_url = "https://social.devnamic.com"
    access_token_token = "abcdefg123456"
    access_token_content = f"{access_token_api_base_url}\n{access_token_client_name}\n{access_token_token}"

    mocked_open_file = MagicMock()
    with patch.object(builtins, "open", mock_open(mock=mocked_open_file, read_data=access_token_content)):
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
    access_token_content = f"{access_token_api_base_url}\n{access_token_client_name}\n{access_token_token}"

    mocked_open_file = MagicMock()
    with patch.object(builtins, "open", mock_open(mock=mocked_open_file, read_data=access_token_content)):
        instance = Firefish(access_token=access_token_filename, api_base_url=instance_api_base_url)

        mocked_open_file.assert_called_once_with(access_token_filename, "r")
        assert instance.api_base_url == instance_api_base_url
        assert instance.client_name == access_token_client_name
        assert instance.bearer_token == access_token_token


def test_log_in_without_password():
    client_id_filename = "client.secret"
    client_id_client_name = "Client"
    client_id_api_base_url = "https://social.devnamic.com"
    client_id_content = f"{client_id_api_base_url}\n{client_id_client_name}"

    mocked_open_file = MagicMock()
    with patch.object(builtins, "open", mock_open(mock=mocked_open_file, read_data=client_id_content)):
        instance = Firefish(client_id=client_id_filename)
        with TestCase.assertRaises(instance, RuntimeError):
            instance.log_in(username="test")

def test_log_in_with_password():
    client_id_filename = "client.secret"
    client_id_client_name = "Client"
    client_id_api_base_url = "https://social.devnamic.com"
    client_id_content = f"{client_id_api_base_url}\n{client_id_client_name}"
    token = "abcdefg123456"
    access_token_filename = "user.secret"
    access_token_filename = "user.secret"
    access_token_client_name = "Client"
    access_token_api_base_url = "https://social.devnamic.com"

    
    with patch.object(builtins, "open", mock_open(read_data=client_id_content)):
        instance = Firefish(client_id=client_id_filename)

    mocked_open_file = MagicMock()
    with patch.object(builtins, "open", mock_open(mock=mocked_open_file)):
        instance.log_in(username="test",
                        password=token,
                        to_file=access_token_filename)

        handle = mocked_open_file()
        handle.write.assert_has_calls(
            [
                call(access_token_api_base_url + "\n"),
                call(access_token_client_name + "\n"),
                call(token)
            ]
        )

        assert instance.bearer_token == token