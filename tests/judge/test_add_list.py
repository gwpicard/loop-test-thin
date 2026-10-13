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
    env = {**os.environ, "HABITS_FILE": str(data_file)}

    def _run(*args):
        return subprocess.run(
            [sys.executable, "-m", "habits", *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    return _run


def test_D1_add_prints_added_and_list_shows_it(run):
    result = run("add", "read")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "added: read"
    listed = run("list")
    assert listed.returncode == 0, listed.stderr
    assert listed.stdout.splitlines() == ["read"]


def test_D2_list_keeps_order_added(run):
    assert run("add", "read").returncode == 0
    assert run("add", "run").returncode == 0
    listed = run("list")
    assert listed.returncode == 0, listed.stderr
    assert listed.stdout.splitlines() == ["read", "run"]


def test_D3_list_with_no_data_file_prints_nothing(run, data_file):
    assert not data_file.exists()
    result = run("list")
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_D4_duplicate_ignoring_case_fails_and_file_unchanged(run, data_file):
    assert run("add", "read").returncode == 0
    before = data_file.read_text()
    result = run("add", "Read")
    assert result.returncode == 1
    assert "habit already exists: read" in result.stderr
    assert data_file.read_text() == before


@pytest.mark.parametrize("name", ["", "   "])
def test_D5_empty_name_fails_and_file_unchanged(run, data_file, name):
    assert run("add", "read").returncode == 0
    before = data_file.read_text()
    result = run("add", name)
    assert result.returncode == 1
    assert "habit name is empty" in result.stderr
    assert data_file.read_text() == before


def test_D6_name_is_trimmed(run):
    result = run("add", "  read  ")
    assert result.returncode == 0, result.stderr
    listed = run("list")
    assert listed.returncode == 0, listed.stderr
    assert listed.stdout.splitlines() == ["read"]
