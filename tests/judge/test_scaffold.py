import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "habits", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_D1_help_exits_zero_and_prints_usage():
    result = run("--help")
    assert result.returncode == 0, result.stderr
    assert any(line.lower().startswith("usage") for line in result.stdout.splitlines())


def test_D2_unknown_command_fails_with_stderr_message():
    result = run("nonsense")
    assert result.returncode != 0
    assert result.stderr.strip() != ""


def test_D3_no_command_fails_and_prints_usage():
    result = run()
    assert result.returncode != 0
    assert "usage" in (result.stdout + result.stderr).lower()


def test_D4_package_imports_from_project_root():
    result = subprocess.run(
        [sys.executable, "-c", "import habits"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
