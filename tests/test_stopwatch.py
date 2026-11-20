from pyxavi import Stopwatch
from unittest.mock import patch
import uuid


def test_start_stop_and_get():
    stopwatch = Stopwatch()

    with patch("time.perf_counter", side_effect=[10.0, 12.5]):
        assert stopwatch.start("a") == "a"
        assert stopwatch.stop("a") == 2.5

    assert stopwatch.get("a") == 2.5


def test_start_without_name_gives_a_uuid_name():
    stopwatch = Stopwatch()

    name = stopwatch.start()

    assert str(uuid.UUID(name)) == name
    assert stopwatch.stop(name) is not None


def test_restart_resets_the_running_stopwatch():
    stopwatch = Stopwatch()

    with patch("time.perf_counter", side_effect=[1.0, 5.0, 6.0]):
        stopwatch.start("a")
        stopwatch.start("a")
        assert stopwatch.stop("a") == 1.0


def test_reset_removes_running_and_stopped_without_breaking_the_instance():
    stopwatch = Stopwatch()
    stopwatch.start("a")
    stopwatch.start("b")
    stopwatch.stop("b")

    stopwatch.reset("a")
    stopwatch.reset("b")

    assert stopwatch._stopwatches_running == {}
    assert stopwatch._stopwatches_stopped == {}
    # It keeps working afterwards
    stopwatch.start("a")
    assert stopwatch.stop("a") is not None


def test_stop_and_get_unknown_give_none():
    stopwatch = Stopwatch()

    assert stopwatch.stop("nope") is None
    assert stopwatch.get("nope") is None


def test_continue_or_start_does_not_restart():
    stopwatch = Stopwatch()

    with patch("time.perf_counter", side_effect=[1.0, 9.0]):
        stopwatch.continue_or_start("a")
        stopwatch.continue_or_start("a")
        assert stopwatch.stop("a") == 8.0


def test_stop_all_stops_every_running_stopwatch():
    stopwatch = Stopwatch()
    stopwatch.start("a")
    stopwatch.start("b")
    stopwatch.start("c")

    stopwatch.stop_all()

    assert stopwatch._stopwatches_running == {}
    assert sorted(stopwatch._stopwatches_stopped) == ["a", "b", "c"]


def test_stop_and_report():
    stopwatch = Stopwatch()
    with patch("time.perf_counter", side_effect=[0.0, 0.0, 1.0, 2.0]):
        stopwatch.start("short")
        stopwatch.start("longer")
        report = stopwatch.stop_and_report()

    assert report.splitlines() == [" short: 1.0", "longer: 2.0"]


def test_clean_removes_everything():
    stopwatch = Stopwatch()
    stopwatch.start("a")
    stopwatch.start("b")
    stopwatch.stop("b")

    stopwatch.clean()

    assert stopwatch._stopwatches_running == {}
    assert stopwatch._stopwatches_stopped == {}


def test_instances_do_not_share_stopwatches():
    first = Stopwatch()
    second = Stopwatch()

    first.start("a")

    assert "a" not in second._stopwatches_running
    assert second.stop("a") is None
