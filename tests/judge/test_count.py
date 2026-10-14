import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(tmp_path, *args):
    env = {"HABITS_FILE": str(tmp_path / "h.json"), "PATH": "/usr/bin:/bin"}
    return subprocess.run([sys.executable, "-m", "habits", *args], cwd=ROOT,
                          capture_output=True, text=True, env=env)


def add_three(tmp_path):
    for name in ("read", "run", "swim"):
        run(tmp_path, "add", name)


def test_D1_count_prints_three(tmp_path):
    add_three(tmp_path)
    assert run(tmp_path, "count").stdout.strip() == "3"


def test_D2_count_prints_zero(tmp_path):
    assert run(tmp_path, "count").stdout.strip() == "0"


def test_D3_count_after_remove(tmp_path):
    add_three(tmp_path)
    run(tmp_path, "remove", "run")
    assert run(tmp_path, "count").stdout.strip() == "2"
