from pyxavi.config import Config
from pyxavi.logger import Logger
from pyxavi.media import Media
from pyxavi.mastodon_publisher import MastodonPublisher, MastodonPublisherException
from pyxavi.mastodon_helper import MastodonHelper,\
    StatusPost, MastodonConnectionParams, MastodonStatusParams
from mastodon import Mastodon
from unittest.mock import patch, Mock, call
import pytest
from logging import Logger as BuildInLogger
from datetime import datetime
import copy
from pyxavi.debugger import dd

CONFIG = {
    "logger": {
        "name": "logger_test"
    },
    "publisher": {
        "media_storage": "storage/media/",
        "dry_run": False,
        "named_account": "test"
    },
    "mastodon": {
        "named_accounts": {
            "mastodon": {
                "app_name": "Mastodon",
                "instance_type": "mastodon",
                "api_base_url": "https://mastodont.cat",
                "credentials": {
                    "user_file": "user.secret",
                    "client_file": "client.secret",
                    "user": {
                        "email": "bot+syscheck@my-fancy.site",
                        "password": "SuperSecureP4ss",
                    }
                },
                "status_params": {
                    "max_length": 5000
                }
            },
            "pleroma": {
                "app_name": "Akkoma",
                "instance_type": "pleroma",
                "api_base_url": "https://mastodont.cat",
                "credentials": {
                    "user_file": "user.secret",
                    "client_file": "client.secret",
                    "user": {
                        "email": "bot+syscheck@my-fancy.site",
                        "password": "SuperSecureP4ss",
                    }
                },
                "status_params": {
                    "max_length": 3000
                }
            },
            "default": {
                "app_name": "Default",
                "instance_type": "firefish",
                "api_base_url": "https://mastodont.cat",
                "credentials": {
                    "user_file": "user.secret",
                    "client_file": "client.secret",
                    "user": {
                        "email": "bot+syscheck@my-fancy.site",
                        "password": "SuperSecureP4ss",
                    }
                },
                "status_params": {
                    "max_length": 500
                }
            },
            "test": {
                "app_name": "Test",
                "instance_type": "firefish",
                "api_base_url": "https://mastodont.cat",
                "credentials": {
                    "user_file": "user.secret",
                    "client_file": "client.secret",
                    "user": {
                        "email": "bot+syscheck@my-fancy.site",
                        "password": "SuperSecureP4ss",
                    }
                },
                "status_params": {
                    "max_length": 500
                }
            }
        }
    }
}


@pytest.fixture(autouse=True)
def setup_function():

    global CONFIG, _mocked_mastodon_instance

    _mocked_mastodon_instance = Mock()
    _mocked_mastodon_instance.__class__ = Mastodon
    _mocked_mastodon_instance.status_post = Mock()
    _mocked_mastodon_instance.status_post.return_value = {"id": 123}
    _mocked_mastodon_instance.media_post = Mock()
    _mocked_mastodon_instance.media_post.return_value = {"id": 456}

    backup = copy.deepcopy(CONFIG)

    yield

    CONFIG = backup


def patch_config_read_file(self):
    self._content = CONFIG

def patch_mastodon_helper_get_instance(connection_params, logger = None, base_path = None):
    return _mocked_mastodon_instance

@patch.object(Config, "read_file", new=patch_config_read_file)
@patch.object(MastodonHelper, "get_instance", new=patch_mastodon_helper_get_instance)
def test_initialize_without_named_account_takes_config():
    config = Config()
    publisher = MastodonPublisher(
        config=config, logger=Logger(config=config).get_logger(), base_path="bla"
    )

    assert isinstance(publisher._connection_params, MastodonConnectionParams)
    dd(publisher._connection_params.app_name)
    dd(publisher._connection_params)
    assert publisher._connection_params.app_name == "Test"


@patch.object(Config, "read_file", new=patch_config_read_file)
@patch.object(MastodonHelper, "get_instance", new=patch_mastodon_helper_get_instance)
def test_initialize_without_named_account_takes_default():
    del CONFIG["publisher"]["named_account"]
    config = Config()
    publisher = MastodonPublisher(
        config=config, logger=Logger(config=config).get_logger(), base_path="bla"
    )

    assert isinstance(publisher._connection_params, MastodonConnectionParams)
    dd(publisher._connection_params.app_name)
    assert publisher._connection_params.app_name == "Default"


@patch.object(Config, "read_file", new=patch_config_read_file)
@patch.object(MastodonHelper, "get_instance", new=patch_mastodon_helper_get_instance)
def get_instance(named_account: str = "mastodon") -> MastodonPublisher:
    
    config = Config()
    return MastodonPublisher(
        config=config, logger=Logger(config=config).get_logger(), named_account=named_account, base_path="bla"
    )


def test_initialize():
    publisher = get_instance()

    assert isinstance(publisher, MastodonPublisher)
    assert isinstance(publisher._config, Config)
    assert isinstance(publisher._logger, BuildInLogger)
    assert isinstance(publisher._mastodon, Mastodon)
    assert isinstance(publisher._connection_params, MastodonConnectionParams)
    assert publisher._connection_params.app_name == "Mastodon"


@pytest.fixture
def text_long() -> str:
    return """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
        do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Risus nullam eget felis eget nunc lobortis mattis. Convallis a
        cras semper auctor neque. Aliquet nec ullamcorper sit amet risus.
        Scelerisque purus semper eget duis at tellus at urna condimentum.
        Urna cursus eget nunc scelerisque viverra mauris. Tortor aliquam
        nulla facilisi cras fermentum odio eu feugiat. Vitae nunc sed velit
        dignissim sodales ut eu sem integer. Viverra adipiscing at in
        tellus. Nunc scelerisque viverra mauris in aliquam sem fringilla
        ut morbi. Sed tempus urna et pharetra pharetra massa massa ultricies.
        Felis imperdiet proin fermentum leo. Felis eget velit aliquet sagittis
        id consectetur purus ut faucibus. Pellentesque sit amet porttitor eget.
        Turpis tincidunt id aliquet risus feugiat in.
    """


def test_do_status_publish_pleroma():
    status_post = StatusPost(status="I am a test")
    publisher = get_instance(named_account="pleroma")
    publisher._is_dry_run = False

    result = publisher._do_status_publish(status_post)

    _mocked_mastodon_instance.status_post.assert_called_once_with(
        status=status_post.status,
        in_reply_to_id=status_post.in_reply_to_id,
        media_ids=status_post.media_ids,
        sensitive=status_post.sensitive,
        visibility=status_post.visibility,
        spoiler_text=status_post.spoiler_text,
        language=status_post.language,
        idempotency_key=status_post.idempotency_key,
        content_type=status_post.content_type,
        scheduled_at=status_post.scheduled_at,
        poll=status_post.poll,
        quote_id=status_post.quote_id
    )
    assert result == {"id": 123}


def test_do_status_publish_mastodon():
    status_post = StatusPost(status="I am a test")
    publisher = get_instance()
    publisher._is_dry_run = False

    result = publisher._do_status_publish(status_post)

    _mocked_mastodon_instance.status_post.assert_called_once_with(
        status=status_post.status,
        in_reply_to_id=status_post.in_reply_to_id,
        media_ids=status_post.media_ids,
        sensitive=status_post.sensitive,
        visibility=status_post.visibility,
        spoiler_text=status_post.spoiler_text,
        language=status_post.language,
        idempotency_key=status_post.idempotency_key,
        scheduled_at=status_post.scheduled_at,
        poll=status_post.poll,
    )
    assert result == {"id": 123}


def test_publish_status_post_not_dry_run_cut_text(text_long: str):
    status_post = StatusPost(status=text_long)
    publisher = get_instance()
    publisher._is_dry_run = False
    publisher._connection_params.status_params.max_length = 500

    result = publisher.publish_status_post(status_post)

    _mocked_mastodon_instance.status_post.assert_called_once_with(
        status=status_post.status[:497] + "...",
        in_reply_to_id=status_post.in_reply_to_id,
        media_ids=status_post.media_ids,
        sensitive=status_post.sensitive,
        visibility=status_post.visibility,
        spoiler_text=status_post.spoiler_text,
        language=status_post.language,
        idempotency_key=status_post.idempotency_key,
        scheduled_at=status_post.scheduled_at,
        poll=status_post.poll,
    )
    assert result == {"id": 123}


def test_publish_status_post_not_dry_run():
    status_post = StatusPost(status="I am a test")
    publisher = get_instance(named_account="pleroma")
    publisher._is_dry_run = False

    mocked_do_status_publish = Mock()
    mocked_do_status_publish.return_value = {"id": 123}
    with patch.object(MastodonPublisher, "_do_status_publish", new=mocked_do_status_publish):
        result = publisher.publish_status_post(status_post)

    mocked_do_status_publish.assert_called_once_with(status_post=status_post)
    assert result == {"id": 123}


def test_publish_status_post_dry_run():
    status_post = StatusPost(status="I am a test")
    publisher = get_instance()
    publisher._is_dry_run = True

    result = publisher.publish_status_post(status_post)

    _mocked_mastodon_instance.status_post.assert_not_called()
    assert result is None

def test_publish_text_not_dry_run():
    text="I am a test"
    publisher = get_instance()
    publisher._is_dry_run = False

    mocked_do_status_publish = Mock()
    mocked_do_status_publish.return_value = {"id": 123}
    with patch.object(MastodonPublisher, "_do_status_publish", new=mocked_do_status_publish):
        result = publisher.publish_text(text)

    call_arguments = mocked_do_status_publish.mock_calls[0][2]
    assert isinstance(call_arguments["status_post"], StatusPost)
    assert call_arguments["status_post"].status == text
    assert call_arguments["status_post"].visibility == publisher._connection_params.status_params.visibility
    assert call_arguments["status_post"].content_type == publisher._connection_params.status_params.content_type
    assert result == {"id": 123}

def test_publish_text_dry_run():
    text="I am a test"
    publisher = get_instance()
    publisher._is_dry_run = True

    result = publisher.publish_text(text)

    _mocked_mastodon_instance.status_post.assert_not_called()
    assert result is None


def test_do_media_publish_download_file():
    media_url = "http://hello.world/img.png"
    media_file = CONFIG["publisher"]["media_storage"] + "/img.png"
    media_mime = "image/png"
    description = "this is an alt text"
    shall_download = True
    downloaded = {"file": media_file, "mime_type": media_mime}

    publisher = get_instance()

    mocked_download_from_url = Mock()
    mocked_download_from_url.return_value = downloaded
    with patch.object(Media, "download_from_url", new=mocked_download_from_url):
        result = publisher._do_media_publish(
            media_file=media_url,
            description=description,
            download_file=shall_download
        )

    mocked_download_from_url.assert_called_once_with(
        media_url, CONFIG["publisher"]["media_storage"]
    )
    _mocked_mastodon_instance.media_post.assert_called_once_with(
        downloaded["file"],
        mime_type=downloaded["mime_type"],
        description=description,
        focus=(0, 1)
    )
    assert result == {"id": 456}


def test_do_media_publish_dont_download_file():
    media_file = CONFIG["publisher"]["media_storage"] + "/img.png"
    media_mime = "image/png"
    description = "this is an alt text"
    shall_download = False
    downloaded = {"file": media_file, "mime_type": media_mime}

    publisher = get_instance()

    mocked_download_from_url = Mock()
    mocked_download_from_url.return_value = downloaded
    with patch.object(Media, "download_from_url", new=mocked_download_from_url):
        result = publisher._do_media_publish(
            media_file=media_file,
            description=description,
            download_file=shall_download,
            mime_type=media_mime
        )

    mocked_download_from_url.assert_not_called()
    _mocked_mastodon_instance.media_post.assert_called_once_with(
        downloaded["file"],
        mime_type=downloaded["mime_type"],
        description=description,
        focus=(0, 1)
    )
    assert result == {"id": 456}


def test_publish_media_dry_run():
    media=[{
        "url": "http://hello.world/img.png"
    }]

    publisher = get_instance()
    publisher._is_dry_run = True

    result = publisher.publish_media(media=media)

    _mocked_mastodon_instance.media_post.assert_not_called()
    assert result == None

def test_publish_media_not_dry_run_url():
    media=[{
        "url": "http://hello.world/img.png"
    }]

    publisher = get_instance()

    mocked_do_media_publish = Mock()
    mocked_do_media_publish.return_value = {"id": 456}
    with patch.object(MastodonPublisher, "_do_media_publish", new=mocked_do_media_publish):
        result = publisher.publish_media(media=media)
    
    mocked_do_media_publish.assert_called_once_with(
        media_file=media[0]["url"],
        download_file=True,
        description=None,
        mime_type=None
    )
    assert result == [456]

def test_publish_media_not_dry_run_path():
    media=[{
        "path": CONFIG["publisher"]["media_storage"] + "/img.png"
    }]

    publisher = get_instance()

    mocked_do_media_publish = Mock()
    mocked_do_media_publish.return_value = {"id": 456}
    with patch.object(MastodonPublisher, "_do_media_publish", new=mocked_do_media_publish):
        result = publisher.publish_media(media=media)
    
    mocked_do_media_publish.assert_called_once_with(
        media_file=media[0]["path"],
        download_file=False,
        description=None,
        mime_type=None
    )
    assert result == [456]

def test_publish_media_not_dry_run_not_url_nor_path():
    media=[CONFIG["publisher"]["media_storage"] + "/img.png"]

    publisher = get_instance()

    mocked_do_media_publish = Mock()
    mocked_do_media_publish.return_value = {"id": 456}
    with patch.object(MastodonPublisher, "_do_media_publish", new=mocked_do_media_publish):
        result = publisher.publish_media(media=media)
    
    mocked_do_media_publish.assert_not_called()
    assert result == []


# def test_publish_status_post_with_media_separated():
#     media
#     status_post = StatusPost(status="I am a test")
#     publisher = get_instance(named_account="pleroma")
#     publisher._is_dry_run = False

#     mocked_do_status_publish = Mock()
#     mocked_do_status_publish.return_value = {"id": 123}
#     with patch.object(MastodonPublisher, "_do_status_publish", new=mocked_do_status_publish):
#         result = publisher.publish_status_post(status_post)

#     mocked_do_status_publish.assert_called_once_with(status_post=status_post)
#     assert result == {"id": 123}