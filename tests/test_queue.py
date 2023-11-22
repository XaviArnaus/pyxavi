from pyxavi.storage import Storage
from pyxavi.dictionary import Dictionary
from pyxavi.item_queue import Queue, SimpleQueueItem
from unittest.mock import patch, Mock
import pytest
from logging import Logger
from datetime import datetime

CONFIG = {"logger.name": "logger_test", "queue_storage.file": "queue.yaml"}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default=None) -> str:
    return CONFIG[param]


def patched_storage_init(self, filename):
    pass


def patched_storage_write(self):
    pass


def patched_storage_get(self, param_name: str = "", default_value: any = None) -> any:
    return []


@pytest.fixture
def datetime_1():
    return datetime(2023, 3, 21)


@pytest.fixture
def datetime_2():
    return datetime(2023, 3, 22)


@pytest.fixture
def datetime_3():
    return datetime(2023, 3, 23)


@pytest.fixture
def queue_item_1(datetime_1):
    return SimpleQueueItem({"text": "one", "date": datetime_1})


@pytest.fixture
def queue_item_2(datetime_2):
    return SimpleQueueItem({"text": "two", "date": datetime_2})


@pytest.fixture
def queue_item_3(datetime_3):
    return SimpleQueueItem({"text": "three", "date": datetime_3})


def patch_storage_read_file(self):
    self._content = []


@patch.object(Storage, "read_file", new=patch_storage_read_file)
def get_stateful_instance():
    return Queue(storage_file="queue.yaml")


def test_stateful_instance():

    queue = get_stateful_instance()

    assert isinstance(queue, Queue)
    assert isinstance(queue._logger, Logger)
    assert isinstance(queue._queue_manager, Storage)
    assert isinstance(queue._queue, list)


def test_stateless_initialize():
    queue = Queue()

    assert isinstance(queue, Queue)
    assert isinstance(queue._logger, Logger)
    assert isinstance(queue._queue_manager, Dictionary)
    assert isinstance(queue._queue, list)


def test_append():
    queue = Queue()
    queue_item = SimpleQueueItem(item="a")

    expected_queue = [queue_item]
    queue.append(queue_item)

    assert queue._queue == expected_queue


def test_sort_by_date(queue_item_1, queue_item_2, queue_item_3):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_3)
    queue.append(queue_item_2)

    current_sorting = list(map(lambda x: x.to_dict()["text"], queue._queue))
    assert current_sorting, ["one", "three", "two"]

    queue.sort(param="date")
    new_sorting = list(map(lambda x: x.to_dict()["text"], queue._queue))
    assert new_sorting, ["one", "two", "three"]


def test_deduplicate(queue_item_1, queue_item_2, queue_item_3):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    current_queue = list(map(lambda x: x.to_dict()["text"], queue._queue))
    assert current_queue, ["one", "two", "two", "three"]

    queue.deduplicate(param="text")
    new_queue = list(map(lambda x: x.to_dict()["text"], queue._queue))
    assert new_queue, ["one", "two", "three"]


def test_save(datetime_1, datetime_2, datetime_3, queue_item_1, queue_item_2, queue_item_3):
    queue = get_stateful_instance()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    mocked_set = Mock()
    mocked_write = Mock()
    with patch.object(Storage, "set", new=mocked_set):
        with patch.object(Storage, "write_file", new=mocked_write):
            queue.save()

    mocked_set.assert_called_once_with(
        "queue",
        [
            {
                "text": "one", "date": datetime_1
            }, {
                "text": "two", "date": datetime_2
            }, {
                "text": "three", "date": datetime_3
            }
        ]
    )
    mocked_write.assert_called_once()


def test_save_stateless(
    datetime_1, datetime_2, datetime_3, queue_item_1, queue_item_2, queue_item_3
):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    mocked_set = Mock()
    mocked_write = Mock()
    with patch.object(Storage, "set", new=mocked_set):
        with patch.object(Storage, "write_file", new=mocked_write):
            queue.save()

    mocked_set.assert_not_called()
    mocked_write.assert_not_called()


def test_is_empty(queue_item_1):
    queue = Queue()

    assert queue.is_empty() is True

    queue.append(queue_item_1)

    assert queue.is_empty() is False

    queue._queue = []

    assert queue.is_empty() is True


def test_get_all(queue_item_1, queue_item_2, queue_item_3):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    current_queue = list(map(lambda x: x.to_dict()["text"], queue.get_all()))
    assert current_queue, ["one", "two", "three"]


def test_clean(queue_item_1, queue_item_2, queue_item_3):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    assert len(queue.get_all()), 3

    queue.clean()

    assert queue.is_empty() is True


def test_pop(queue_item_1, queue_item_2, queue_item_3):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    assert len(queue.get_all()), 3

    queue_item = queue.pop()

    assert queue_item, queue_item_1
    assert len(queue.get_all()), 2


def test_unpop(queue_item_1, queue_item_2, queue_item_3):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_2)

    assert len(queue.get_all()), 2

    queue.unpop(item=queue_item_3)

    stack = queue.get_all()
    assert len(stack), 3
    # The unpop() should add it at the beginning
    assert stack[0] == queue_item_3
    assert stack[1] == queue_item_1
    assert stack[2] == queue_item_2


def test_first(queue_item_1, queue_item_2, queue_item_3):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    assert len(queue.get_all()), 3

    queue_item = queue.first()

    assert queue_item, queue_item_1
    assert len(queue.get_all()), 3


def test_last(queue_item_1, queue_item_2, queue_item_3):
    queue = Queue()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    assert len(queue.get_all()), 3

    queue_item = queue.last()

    assert queue_item, queue_item_3
    assert len(queue.get_all()), 3
