import os
import subprocess
import sys

# Dependencies that are only needed when some feature is used
LAZY_MODULES = [
    "requests", "bs4", "feedparser", "validators", "emoji", "multiprocessing_logging"
]


def test_importing_pyxavi_does_not_import_the_heavy_dependencies():
    code = (
        "import sys, pyxavi\n"
        f"print(','.join(m for m in {LAZY_MODULES!r} if m in sys.modules))"
    )
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)}

    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, check=True
    )

    assert result.stdout.strip() == ""


def test_the_public_names_are_still_exported():
    import pyxavi

    names = ["Media", "Network", "Url", "Janitor", "Text", "Logger", "Stopwatch", "Storage"]
    for name in names:
        assert hasattr(pyxavi, name)
