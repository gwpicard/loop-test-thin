# Intent: `habits done` and `habits remove` reject a blank name with `habit name is empty`, like `habits add`.
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


def test_D1_done_blank_name_rejected(run, data_file):
    assert run("add", "read").returncode == 0
    before = data_file.read_text()
    result = run("done", "  ")
    assert result.returncode == 1
    assert result.stderr.strip() == "habit name is empty"
    assert data_file.read_text() == before


def test_D2_remove_blank_name_rejected(run, data_file):
    assert run("add", "read").returncode == 0
    before = data_file.read_text()
    result = run("remove", "")
    assert result.returncode == 1
    assert result.stderr.strip() == "habit name is empty"
    assert data_file.read_text() == before


def test_D3_done_unknown_habit_still_reports_no_such_habit(run, data_file):
    assert run("add", "read").returncode == 0
    before = data_file.read_text()
    result = run("done", "swim")
    assert result.returncode == 1
    assert result.stderr.strip() == "no such habit: swim"
    assert data_file.read_text() == before
