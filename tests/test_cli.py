import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bsky2masto", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_version_flag_works():
    result = _run_cli("--version")
    assert result.returncode == 0
    assert "bsky2masto" in result.stdout


def test_cli_help_flag_works():
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "--actor" in result.stdout
