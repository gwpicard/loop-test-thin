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


def test_D1_remove_prints_removed_and_list_drops_it(run):
    assert run("add", "read").returncode == 0
    result = run("remove", "read")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "removed: read"
    listed = run("list")
    assert listed.returncode == 0, listed.stderr
    assert "read" not in listed.stdout.splitlines()


def test_D2_remove_ignores_case_and_prints_saved_name(run):
    assert run("add", "read").returncode == 0
    result = run("remove", "READ")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "removed: read"


def test_D3_unknown_habit_fails_and_file_unchanged(run, data_file):
    assert run("add", "read").returncode == 0
    before = data_file.read_text()
    result = run("remove", "swim")
    assert result.returncode == 1
    assert "no such habit: swim" in result.stderr
    assert data_file.read_text() == before


def test_D4_other_habits_keep_order_and_done_days(run, data_file):
    data_file.write_text(
        json.dumps(
            [
                {"name": "read", "done": ["2026-01-01"]},
                {"name": "run", "done": ["2026-01-01", "2026-01-02"]},
                {"name": "swim", "done": []},
            ]
        )
    )
    result = run("remove", "run")
    assert result.returncode == 0, result.stderr
    assert json.loads(data_file.read_text()) == [
        {"name": "read", "done": ["2026-01-01"]},
        {"name": "swim", "done": []},
    ]


def test_D5_removed_name_can_be_added_again(run):
    assert run("add", "read").returncode == 0
    removed = run("remove", "read")
    assert removed.returncode == 0, removed.stderr
    again = run("add", "read")
    assert again.returncode == 0, again.stderr
    assert again.stdout.strip() == "added: read"
