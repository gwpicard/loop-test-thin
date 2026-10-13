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


def seed(data_file, habits):
    data_file.write_text(
        json.dumps([{"name": n, "done": d} for n, d in habits])
    )


def streaks(run, today):
    result = run("list", "--streaks", today=today)
    assert result.returncode == 0, result.stderr
    return result.stdout.splitlines()


def test_D1_streaks_flag_prints_name_and_count_in_order(run):
    assert run("add", "read").returncode == 0
    assert run("add", "run").returncode == 0
    assert streaks(run, "2026-01-01") == ["read: 0", "run: 0"]


def test_D2_streak_counts_days_in_a_row_ending_today(run, data_file):
    seed(data_file, [("read", ["2026-01-01", "2026-01-02", "2026-01-03"])])
    assert streaks(run, "2026-01-03") == ["read: 3"]


def test_D3_streak_still_counts_when_last_done_is_yesterday(run, data_file):
    seed(data_file, [("read", ["2026-01-01", "2026-01-02"])])
    assert streaks(run, "2026-01-03") == ["read: 2"]


def test_D4_gap_resets_streak(run, data_file):
    seed(data_file, [("read", ["2026-01-01", "2026-01-03"])])
    assert streaks(run, "2026-01-03") == ["read: 1"]


def test_D5_old_last_done_day_gives_zero(run, data_file):
    seed(data_file, [("read", ["2026-01-01", "2026-01-02"])])
    assert streaks(run, "2026-01-04") == ["read: 0"]

