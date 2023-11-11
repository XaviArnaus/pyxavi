from __future__ import annotations
from pyxavi.config import Config
from pyxavi.storage import Storage
# from janitor.objects.queue_item import QueueItem
from typing import Protocol
import logging
import os


class QueueItemProtocol(Protocol):

    def to_dict(self) -> dict:
        """Convert the object into a dict"""

    @staticmethod
    def from_dict(dictionary: dict) -> QueueItemProtocol:
        """Instantiates this class from a given dictionary"""

    def sort_value(self, param: any = None) -> any:
        """Returns a value that will be used to sort the collection of self items"""

    def unique_value(self, param: any = None) -> any:
        """Returns a value that will be used to deduplicate the collection of self items"""


class SimpleQueueItem(QueueItemProtocol):

    item: dict = None

    def __init__(self, item: dict) -> None:
        self.item = item
        super().__init__()

    def to_dict(self) -> dict:
        return self.item

    @staticmethod
    def from_dict(dictionary: dict) -> QueueItemProtocol:
        return SimpleQueueItem(item=dictionary)

    def sort_value(self, param: any = None) -> any:
        return self.item[param] if param in self.item else None

    def unique_value(self, param: any = None) -> any:
        return self.item[param] if param in self.item else None


class Queue:

    DEFAULT_STORAGE_FILE = "storage/queue.yaml"
    _queue = []

    def __init__(self, config: Config, base_path: str = None) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self.__storage_file = config.get("queue_storage.file", self.DEFAULT_STORAGE_FILE)
        if base_path is not None:
            self.__storage_file = os.path.join(base_path, self.__storage_file)
        self.load()

    def load(self) -> int:
        self._queue_manager = Storage(filename=self.__storage_file)
        self._queue = list(
            map(lambda x: QueueItemProtocol.from_dict(x), self._queue_manager.get("queue", []))
        )
        return self.length()

    def append(self, item: QueueItemProtocol) -> None:
        self._queue.append(item)

    def sort(self, param: any = None) -> None:
        self._logger.debug("Sorting queue by date ASC")
        self._queue = sorted(self._queue, key=lambda x: x.sort_value(param=param))

    def deduplicate(self, param: any = None) -> None:
        self._logger.debug("Deduplicating queue")
        uniques_queue = []
        output_queue = []
        [
            output_queue.append(x) and uniques_queue.append(x.unique_value(param=param))
            for x in self._queue if x.unique_value(param=param) not in uniques_queue
        ]
        self._queue = output_queue

    def save(self) -> None:
        self._logger.debug("Saving the queue")
        self._queue_manager.set("queue", list(map(lambda x: x.to_dict(), self._queue)))
        self._queue_manager.write_file()

    # def update(self, param: any = None) -> None:
    #     self.sort(param=param)
    #     self.deduplicate()
    #     self.save()

    def is_empty(self) -> bool:
        return False if self._queue else True

    def get_all(self) -> list:
        return self._queue

    def clean(self) -> None:
        self._queue = []

    def length(self) -> int:
        return len(self._queue)

    def pop(self) -> dict:
        return self._queue.pop(0) if not self.is_empty() else None

    def unpop(self, item: QueueItemProtocol) -> None:
        if self.is_empty():
            self._queue = []

        self._queue = [item] + self._queue

    def first(self) -> dict:
        return self._queue[0] if not self.is_empty() else None

    def last(self) -> dict:
        return self._queue[-1] if not self.is_empty() else None
