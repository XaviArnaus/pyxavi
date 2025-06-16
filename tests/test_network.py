from pyxavi import Network, EXTERNAL_SERVICE_IPv4, EXTERNAL_SERVICE_IPv6
from unittest.mock import Mock, patch, call
import pytest
import logging
import requests


@pytest.mark.parametrize(
    argnames=('address', 'expected_result'),
    argvalues=[
        ("192.168.0.1", True),
        ("89.247.157.11", True),
        ("289.247.157.11", False),
        ("aa.247.157.11", False),
    ],
)
def test_is_valid_ipv4(address, expected_result):
    assert Network.is_valid_ipv4(address=address) is expected_result


@pytest.mark.parametrize(
    argnames=('address', 'expected_result'),
    argvalues=[
        ("2001:db8:3333:4444:5555:6666:7777:8888", True),
        ("2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF", True),
        ("20012:db8:3333:4444:CCCC:DDDD:EEEE:FFFF", False),
        ("test", False),
    ],
)
def test_is_valid_ipv6(address, expected_result):
    assert Network.is_valid_ipv6(address=address) is expected_result


def test_get_external_ipv4_first_call_success_no_log():
    test_address = "1.1.1.1"

    class Response:
        status_code: int
        text: str
        reason: str

        def __init__(self, status_code: int, text: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.text = text
            self.reason = reason

    mocked_requests_request = Mock()
    mocked_requests_request.return_value = Response(status_code=200, text=test_address)
    mocked_validator = Mock()
    mocked_validator.return_value = True
    with patch.object(requests, "get", new=mocked_requests_request):
        with patch.object(Network, "is_valid_ipv4", new=mocked_validator):
            address = Network.get_external_ipv4()

            mocked_requests_request.assert_called_once_with(EXTERNAL_SERVICE_IPv4["ipfy IPv4"])

            assert address == test_address


def test_get_external_ipv4_first_call_success_with_log():
    test_address = "1.1.1.1"
    logger = logging.getLogger()

    class Response:
        status_code: int
        text: str
        reason: str

        def __init__(self, status_code: int, text: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.text = text
            self.reason = reason

    mocked_requests_request = Mock()
    mocked_requests_request.return_value = Response(status_code=200, text=test_address)
    mocked_validator = Mock()
    mocked_validator.return_value = True
    mocked_logger_debug = Mock()
    with patch.object(requests, "get", new=mocked_requests_request):
        with patch.object(Network, "is_valid_ipv4", new=mocked_validator):
            with patch.object(logger, "debug", new=mocked_logger_debug):
                address = Network.get_external_ipv4(logger=logger)

                mocked_requests_request.assert_called_once_with(
                    EXTERNAL_SERVICE_IPv4["ipfy IPv4"]
                )

                mocked_logger_debug.assert_has_calls(
                    [
                        call("Getting external IP from ipfy IPv4"),
                        call(f"External IP: {test_address}")
                    ]
                )

                assert address == test_address


def test_get_external_ipv4_second_call_success_no_log():
    test_address = "1.1.1.1"

    class Response:
        status_code: int
        text: str
        reason: str

        def __init__(self, status_code: int, text: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.text = text
            self.reason = reason

    mocked_requests_request = Mock()
    mocked_requests_request.side_effect = [
        Response(status_code=429, reason="Too Many Requests"),
        Response(status_code=200, text=test_address)
    ]
    mocked_validator = Mock()
    mocked_validator.return_value = True
    with patch.object(requests, "get", new=mocked_requests_request):
        with patch.object(Network, "is_valid_ipv4", new=mocked_validator):
            address = Network.get_external_ipv4()

            mocked_requests_request.assert_has_calls(
                [
                    call(EXTERNAL_SERVICE_IPv4["ipfy IPv4"]),
                    call(EXTERNAL_SERVICE_IPv4["ident.me IPv4"])
                ]
            )

            assert address == test_address


def test_get_external_ipv4_second_call_success_with_log():
    test_address = "1.1.1.1"
    logger = logging.getLogger()

    class Response:
        status_code: int
        text: str
        reason: str

        def __init__(self, status_code: int, text: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.text = text
            self.reason = reason

    mocked_requests_request = Mock()
    mocked_requests_request.side_effect = [
        Response(status_code=429, reason="Too Many Requests"),
        Response(status_code=200, text=test_address)
    ]
    mocked_validator = Mock()
    mocked_validator.return_value = True
    mocked_logger_debug = Mock()
    mocked_logger_warning = Mock()
    with patch.object(requests, "get", new=mocked_requests_request):
        with patch.object(Network, "is_valid_ipv4", new=mocked_validator):
            with patch.object(logger, "debug", new=mocked_logger_debug):
                with patch.object(logger, "warning", new=mocked_logger_warning):
                    address = Network.get_external_ipv4(logger=logger)

                    mocked_requests_request.assert_has_calls(
                        [
                            call(EXTERNAL_SERVICE_IPv4["ipfy IPv4"]),
                            call(EXTERNAL_SERVICE_IPv4["ident.me IPv4"])
                        ]
                    )

                    mocked_logger_debug.assert_has_calls(
                        [
                            call("Getting external IP from ipfy IPv4"),
                            call("Getting external IP from ident.me IPv4"),
                            call(f"External IP: {test_address}")
                        ]
                    )

                    url = EXTERNAL_SERVICE_IPv4["ipfy IPv4"]
                    mocked_logger_warning.assert_called_once_with(
                        f"{url} answered with an error -> 429: Too Many Requests"
                    )

                    assert address == test_address


def test_get_external_ipv6_first_call_success_no_log():
    test_address = "2001:db8:3333:4444:5555:6666:7777:8888"

    class Response:
        status_code: int
        text: str
        reason: str

        def __init__(self, status_code: int, text: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.text = text
            self.reason = reason

    mocked_requests_request = Mock()
    mocked_requests_request.return_value = Response(status_code=200, text=test_address)
    mocked_validator = Mock()
    mocked_validator.return_value = True
    with patch.object(requests, "get", new=mocked_requests_request):
        with patch.object(Network, "is_valid_ipv6", new=mocked_validator):
            address = Network.get_external_ipv6()

            mocked_requests_request.assert_called_once_with(
                EXTERNAL_SERVICE_IPv6["ident.me IPv6"]
            )

            assert address == test_address


def test_get_external_ipv6_second_call_success_with_log():
    test_address = "2001:db8:3333:4444:5555:6666:7777:8888"
    logger = logging.getLogger()

    class Response:
        status_code: int
        text: str
        reason: str

        def __init__(self, status_code: int, text: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.text = text
            self.reason = reason

    mocked_requests_request = Mock()
    mocked_requests_request.return_value = Response(status_code=200, text=test_address)
    mocked_validator = Mock()
    mocked_validator.return_value = True
    mocked_logger_debug = Mock()
    with patch.object(requests, "get", new=mocked_requests_request):
        with patch.object(Network, "is_valid_ipv6", new=mocked_validator):
            with patch.object(logger, "debug", new=mocked_logger_debug):
                address = Network.get_external_ipv6(logger=logger)

                mocked_requests_request.assert_called_once_with(
                    EXTERNAL_SERVICE_IPv6["ident.me IPv6"]
                )

                mocked_logger_debug.assert_has_calls(
                    [
                        call("Getting external IP from ident.me IPv6"),
                        call(f"External IP: {test_address}")
                    ]
                )

                assert address == test_address
