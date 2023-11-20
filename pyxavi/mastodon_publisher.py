from __future__ import annotations
from pyxavi.config import Config
from pyxavi.media import Media
from pyxavi.terminal_color import TerminalColor
from pyxavi.mastodon_helper import MastodonHelper, StatusPost, MastodonConnectionParams
from logging import Logger
import time


class MastodonPublisher:
    '''
    MastodonPublisherException

    It is responsible to publish status posts.
    '''

    MAX_RETRIES = 3
    SLEEP_TIME = 10
    DEFAULT_NAMED_ACCOUNT = "default"

    def __init__(
        self,
        config: Config,
        logger: Logger,
        named_account: str = None,
        base_path: str = None
    ) -> None:
        self._config = config
        self._logger = logger

        if named_account is None:
            named_account = config.get("publisher.named_account", self.DEFAULT_NAMED_ACCOUNT)
        self._connection_params = MastodonConnectionParams.from_dict(
            config.get(f"mastodon.named_accounts.{named_account}")
        )
        self._instance_type = MastodonHelper.valid_or_raise(
            self._connection_params.instance_type
        )
        self._is_dry_run = config.get("publisher.dry_run", False)
        self._media_storage = config.get("publisher.media_storage")

        self._mastodon = MastodonHelper.get_instance(
            connection_params=self._connection_params, logger=self._logger, base_path=base_path
        )

    def _post_media(self, media_file: str, description: str) -> dict:
        try:
            downloaded = Media().download_from_url(media_file, self._media_storage)
            return self._mastodon.media_post(
                downloaded["file"], mime_type=downloaded["mime_type"], description=description
            )
        except Exception as e:
            self._logger.exception(e)

    def publish_text(self, text: str) -> dict:
        return self.publish_status_post(
            status_post=StatusPost(
                status=text,
                visibility=self._connection_params.status_params.visibility,
                content_type=self._connection_params.status_params.content_type,
            )
        )

    def publish_status_post(self, status_post: StatusPost) -> dict:
        if self._is_dry_run:
            self._logger.debug("It's a Dry Run, stopping here.")
            return None

        # posted_media = []
        # if "media" in item and item["media"]:
        #     self._logger.info("Publising first %s media items", len(item["media"]))
        #     for item in item["media"]:
        #         posted_result = self._post_media(
        #             item["url"],
        #             description=item["alt_text"] if "alt_text" in item else None
        #         )
        #         if posted_result:
        #             posted_media.append(posted_result["id"])
        #         else:
        #             self._logger.info("Could not publish %s", item["url"])

        # Let's ensure that it fits according to the params
        status_post.status = self.__slice_status_if_longer_than_defined(
            status=status_post.status
        )

        retry = 0
        published = None
        while published is None:
            try:
                self._logger.info(
                    f"{TerminalColor.CYAN}Publishing new post (retry {retry}) for " +
                    f"instance type {self._instance_type} and account " +
                    f"{self._connection_params.app_name}{TerminalColor.END}"
                )
                published = self._do_status_publish(status_post=status_post)
                return published
            except Exception as e:
                self._logger.exception(e)
                self._logger.debug(f"sleeping {self.SLEEP_TIME} seconds")
                time.sleep(self.SLEEP_TIME)
                retry += 1
                if retry >= self.MAX_RETRIES:
                    self._logger.error(
                        f"{TerminalColor.RED_BRIGHT}MAX RETRIES of {self.MAX_RETRIES}" +
                        f" is reached. Stop trying.{TerminalColor.END}"
                    )
                    raise MastodonPublisherException(f"Could not publish the post: {e}")

    def _do_status_publish(self, status_post: StatusPost) -> dict:
        """
        This is the method that executes the post of the status.

        No checks, no validations, just the action.
        """

        if self._instance_type == MastodonHelper.TYPE_MASTODON:
            published = self._mastodon.status_post(
                status=status_post.status,
                in_reply_to_id=status_post.in_reply_to_id,
                media_ids=status_post.media_ids,
                sensitive=status_post.sensitive,
                visibility=status_post.visibility,
                spoiler_text=status_post.spoiler_text,
                language=status_post.language,
                idempotency_key=status_post.idempotency_key,
                scheduled_at=status_post.scheduled_at,
                poll=status_post.poll
            )
        elif self._instance_type == MastodonHelper.TYPE_PLEROMA:
            published = self._mastodon.status_post(
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
        elif self._instance_type == MastodonHelper.TYPE_FIREFISH:
            published = self._mastodon.status_post(
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
        else:
            raise RuntimeError(f"Unknown instance type {self._instance_type}")
        return published

    def __slice_status_if_longer_than_defined(self, status: str) -> str:
        max_length = self._connection_params.status_params.max_length
        if len(status) > max_length:
            self._logger.debug(
                f"The status post is longer than the max length of {max_length}. Cutting..."
            )
            status = status[:max_length - 3] + "..."

        return status


class MastodonPublisherException(BaseException):
    pass
