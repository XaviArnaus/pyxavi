from pyxavi.mastodon_helper import MastodonHelper, MastodonConnectionParams
from unittest.mock import patch, Mock, call
from unittest import TestCase
import pytest
from mastodon import Mastodon
import logging
import os

CONFIG_MASTODON_CONN_PARAMS = {
    "app_name": "SuperApp",
    "instance_type": "mastodon",
    "api_base_url": "https://mastodont.cat",
    "credentials": {
        "user_file": "user.secret",
        "client_file": "client.secret",
        "user": {
            "email": "bot+syscheck@my-fancy.site",
            "password": "SuperSecureP4ss",
        }
    }
}


@pytest.mark.parametrize(
    argnames=('value', 'expected_type', 'expected_exception'),
    argvalues=[
        ("mastodon", MastodonHelper.TYPE_MASTODON, False),
        ("pleroma", MastodonHelper.TYPE_PLEROMA, False),
        ("firefish", MastodonHelper.TYPE_FIREFISH, False),
        ("exception", None, RuntimeError),
    ],
)
def test_message_type_valid_or_raise(value, expected_type, expected_exception):
    if expected_exception:
        with TestCase.assertRaises(MastodonHelper, expected_exception):
            instanciated_type = MastodonHelper.valid_or_raise(value=value)
    else:
        instanciated_type = MastodonHelper.valid_or_raise(value=value)
        assert instanciated_type, expected_type


def test_get_instance_mastodon_user_credentials_exists_no_logger():
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "mastodon"
    mocked_path_exists = Mock()
    mocked_path_exists.side_effect = [True, True]
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
            instance = MastodonHelper.get_instance(
                connection_params=conn_params
            )

    mocked_path_exists.assert_has_calls([
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"]),
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]),
    ])
    mocked_mastodon_init.assert_called_once_with(
        access_token=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"],
        feature_set="mainline"
    )
    assert isinstance(instance, Mastodon)


def test_get_instance_mastodon_user_credentials_exists():
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "mastodon"
    mocked_path_exists = Mock()
    mocked_path_exists.side_effect = [True, True]
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
            instance = MastodonHelper.get_instance(
                logger=logging.getLogger(), connection_params=conn_params
            )

    mocked_path_exists.assert_has_calls([
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"]),
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]),
    ])
    mocked_mastodon_init.assert_called_once_with(
        access_token=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"],
        feature_set="mainline"
    )
    assert isinstance(instance, Mastodon)


def test_get_instance_pleroma_user_credentials_exists():
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "pleroma"
    mocked_path_exists = Mock()
    mocked_path_exists.side_effect = [True, True]
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
            instance = MastodonHelper.get_instance(
                logger=logging.getLogger(), connection_params=conn_params
            )

    mocked_path_exists.assert_has_calls([
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"]),
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]),
    ])
    mocked_mastodon_init.assert_called_once_with(
        access_token=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"],
        feature_set="pleroma"
    )
    assert isinstance(instance, Mastodon)


def test_get_instance_mastodon_user_credentials_not_exists():
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "mastodon"
    mocked_path_exists = Mock()
    mocked_path_exists.side_effect = [True, False]
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    mocked_mastodon_log_in = Mock()
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            with patch.object(Mastodon, "log_in", new=mocked_mastodon_log_in):
                conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
                instance = MastodonHelper.get_instance(
                    logger=logging.getLogger(), connection_params=conn_params
                )

    mocked_path_exists.assert_has_calls([
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"]),
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]),
    ])
    mocked_mastodon_init.assert_called_once_with(
        client_id=CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"],
        api_base_url=CONFIG_MASTODON_CONN_PARAMS["api_base_url"],
        feature_set="mainline"
    )
    mocked_mastodon_log_in.assert_called_once_with(
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user"]["email"],
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user"]["password"],
        to_file=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]
    )
    assert isinstance(instance, Mastodon)


def test_get_instance_pleroma_user_credentials_not_exists():
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "pleroma"
    mocked_path_exists = Mock()
    mocked_path_exists.side_effect = [True, False]
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    mocked_mastodon_log_in = Mock()
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            with patch.object(Mastodon, "log_in", new=mocked_mastodon_log_in):
                conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
                instance = MastodonHelper.get_instance(
                    logger=logging.getLogger(), connection_params=conn_params
                )

    mocked_path_exists.assert_has_calls([
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"]),
        call( CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]),
    ])
    mocked_mastodon_init.assert_called_once_with(
        client_id=CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"],
        api_base_url=CONFIG_MASTODON_CONN_PARAMS["api_base_url"],
        feature_set="pleroma"
    )
    mocked_mastodon_log_in.assert_called_once_with(
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user"]["email"],
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user"]["password"],
        to_file=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]
    )
    assert isinstance(instance, Mastodon)
