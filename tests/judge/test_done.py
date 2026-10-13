import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def data_file(tmp_path):
    return tmp_path / "habits.json"


@pytest.fixture
def run(data_file):
    def _run(*args, today="2026-01-01"):
        env = {**os.environ, "HABITS_FILE": str(data_file), "HABITS_TODAY": today}
        return subprocess.run(
            [sys.executable, "-m", "habits", *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    return _run


def test_D1_done_prints_done_and_exits_0(run):
    assert run("add", "read").returncode == 0
    result = run("done", "read")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "done: read"


def test_D2_unknown_habit_fails_and_file_unchanged(run, data_file):
    assert run("add", "read").returncode == 0
    before = data_file.read_text()
    result = run("done", "swim")
    assert result.returncode == 1
    assert "no such habit: swim" in result.stderr
    assert data_file.read_text() == before


def test_D3_done_twice_same_day_is_noop(run, data_file):
    assert run("add", "read").returncode == 0
    first = run("done", "read")
    assert first.returncode == 0, first.stderr
    before = data_file.read_text()
    second = run("done", "read")
    assert second.returncode == 0, second.stderr
    assert second.stdout.strip() == "already done today: read"
    assert data_file.read_text() == before


def test_D4_done_ignores_case_and_prints_saved_name(run):
    assert run("add", "read").returncode == 0
    result = run("done", "READ")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "done: read"


def test_D5_new_day_allows_new_mark(run):
    assert run("add", "read").returncode == 0
    day1 = run("done", "read", today="2026-01-01")
    assert day1.returncode == 0, day1.stderr
    assert day1.stdout.strip() == "done: read"
    day2 = run("done", "read", today="2026-01-02")
    assert day2.returncode == 0, day2.stderr
    assert day2.stdout.strip() == "done: read"


def test_D6_old_format_file_still_works(run, data_file):
    data_file.write_text(json.dumps(["read", "run"]))
    result = run("done", "read")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "done: read"
    listed = run("list")
    assert listed.returncode == 0, listed.stderr
    assert listed.stdout.splitlines() == ["read", "run"]
