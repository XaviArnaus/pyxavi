from pyxavi import Janitor
from unittest.mock import Mock, patch
import pytest
import requests
import socket


def test_initialize_with_hostname():
    remote_url = "https://i.am.an.url:5000"
    hostname_param = "endor"
    hostname_socket = "alderaan"

    mocked_socket_gethostname = Mock()
    mocked_socket_gethostname.return_value = hostname_socket

    with patch.object(socket, "gethostname", new=mocked_socket_gethostname):
        instance = Janitor(remote_url=remote_url, hostname=hostname_param)

    mocked_socket_gethostname.assert_not_called()
    assert isinstance(instance, Janitor) is True
    assert instance._remote_url == remote_url
    assert instance._hostname == hostname_param


def test_initialize_without_hostname():
    remote_url = "https://i.am.an.url:5000"
    hostname_socket = "alderaan"

    mocked_socket_gethostname = Mock()
    mocked_socket_gethostname.return_value = hostname_socket

    with patch.object(socket, "gethostname", new=mocked_socket_gethostname):
        instance = Janitor(remote_url=remote_url)

    mocked_socket_gethostname.assert_called_once()
    assert isinstance(instance, Janitor) is True
    assert instance._remote_url == remote_url
    assert instance._hostname == hostname_socket


@pytest.mark.parametrize(
    argnames=('call', 'message_type', 'message', 'summary', 'expected_result'),
    argvalues=[
        ("log", Janitor.MessageType.NONE, "I am a message", None, 200),
        ("log", Janitor.MessageType.NONE, "I am a message", "I am a summary", 200),
        ("info", Janitor.MessageType.INFO, "I am a message", None, 200),
        ("info", Janitor.MessageType.INFO, "I am a message", "I am a summary", 200),
        ("warning", Janitor.MessageType.WARNING, "I am a message", None, 200),
        ("warning", Janitor.MessageType.WARNING, "I am a message", "I am a summary", 200),
        ("error", Janitor.MessageType.ERROR, "I am a message", None, 200),
        ("error", Janitor.MessageType.ERROR, "I am a message", "I am a summary", 200),
        ("alarm", Janitor.MessageType.ALARM, "I am a message", None, 200),
        ("alarm", Janitor.MessageType.ALARM, "I am a message", "I am a summary", 200),
    ],
)
def test_messaging(call, message_type, message, summary, expected_result):

    class ObjectFaker:

        def __init__(self, d: dict):
            for key, value in d.items():
                setattr(self, key, value)

    hostname = "hostname"
    remote_url = "https://i.am.an.url:5000"

    expected_params = {
        "hostname": hostname, "message": message, "message_type": str(message_type)
    }
    if summary is not None:
        expected_params["summary"] = summary

    mocked_requests_post = Mock()
    mocked_requests_post.return_value = ObjectFaker({"status_code": expected_result})

    instance = Janitor(remote_url=remote_url, hostname=hostname)

    with patch.object(requests, "post", new=mocked_requests_post):
        if call == "log":
            result = instance.log(message=message, summary=summary)
        elif call == "info":
            result = instance.info(message=message, summary=summary)
        elif call == "warning":
            result = instance.warning(message=message, summary=summary)
        elif call == "error":
            result = instance.error(message=message, summary=summary)
        elif call == "alarm":
            result = instance.alarm(message=message, summary=summary)

    assert result == expected_result
    mocked_requests_post.assert_called_once_with(f"{remote_url}/message", data=expected_params)
