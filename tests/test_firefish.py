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

