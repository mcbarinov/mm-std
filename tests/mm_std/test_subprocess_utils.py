"""Tests for subprocess_utils module."""

import pytest

from mm_std.subprocess_utils import TIMEOUT_EXIT_CODE, CmdResult, run_cmd


class TestCmdResult:
    """Tests for CmdResult dataclass properties."""

    def test_combined_output_both(self) -> None:
        """Returns stdout and stderr joined with newline."""
        result = CmdResult(stdout="out", stderr="err", code=0)
        assert result.combined_output == "out\nerr"

    def test_combined_output_stdout_only(self) -> None:
        """Returns stdout without trailing newline when no stderr."""
        result = CmdResult(stdout="out", stderr="", code=0)
        assert result.combined_output == "out"

    def test_combined_output_stderr_only(self) -> None:
        """Returns stderr when stdout is empty."""
        result = CmdResult(stdout="", stderr="err", code=0)
        assert result.combined_output == "err"

    def test_combined_output_empty(self) -> None:
        """Returns empty string when both are empty."""
        result = CmdResult(stdout="", stderr="", code=0)
        assert result.combined_output == ""

    @pytest.mark.parametrize("code", [0])
    def test_is_success_true(self, code: int) -> None:
        """Returns True when exit code is 0."""
        result = CmdResult(stdout="", stderr="", code=code)
        assert result.is_success is True

    @pytest.mark.parametrize("code", [1, 2, 127, 255])
    def test_is_success_false(self, code: int) -> None:
        """Returns False when exit code is non-zero."""
        result = CmdResult(stdout="", stderr="", code=code)
        assert result.is_success is False

    @pytest.mark.parametrize("code", [TIMEOUT_EXIT_CODE])
    def test_is_timeout_true(self, code: int) -> None:
        """Returns True when exit code is TIMEOUT_EXIT_CODE (255)."""
        result = CmdResult(stdout="", stderr="", code=code)
        assert result.is_timeout is True

    @pytest.mark.parametrize("code", [0, 1, 2, 127, 254])
    def test_is_timeout_false(self, code: int) -> None:
        """Returns False when exit code is not TIMEOUT_EXIT_CODE."""
        result = CmdResult(stdout="", stderr="", code=code)
        assert result.is_timeout is False


class TestRunCmd:
    """Tests for run_cmd function with real command execution."""

    def test_successful_command(self) -> None:
        """Simple command returns exit code 0."""
        result = run_cmd("echo hello")
        assert result.code == 0
        assert result.is_success is True

    def test_failed_command(self) -> None:
        """Command that fails returns non-zero exit code."""
        result = run_cmd("ls /nonexistent_path_12345")
        assert result.code != 0
        assert result.is_success is False

    def test_captures_stdout(self) -> None:
        """Stdout is captured correctly."""
        result = run_cmd("echo hello")
        assert result.stdout.strip() == "hello"

    def test_captures_stderr(self) -> None:
        """Stderr is captured correctly."""
        result = run_cmd("ls /nonexistent_path_12345")
        assert result.stderr != ""
        assert "nonexistent" in result.stderr.lower() or "no such" in result.stderr.lower()

    def test_timeout(self) -> None:
        """Long-running command times out with code 255 and stderr='timeout'."""
        result = run_cmd("sleep 10", timeout=1)
        assert result.code == TIMEOUT_EXIT_CODE
        assert result.is_timeout is True
        assert result.stderr == "timeout"

    def test_shell_mode_pipes(self) -> None:
        """Pipe commands work with shell=True."""
        result = run_cmd("echo hello | cat", shell=True)
        assert result.code == 0
        assert result.stdout.strip() == "hello"

    def test_safe_mode_no_shell_interpretation(self) -> None:
        """Special chars are treated literally with shell=False."""
        # With shell=False, the pipe character is passed as an argument to echo
        result = run_cmd("echo hello | cat", shell=False)
        assert result.code == 0
        # The output will contain the literal "| cat" as echo arguments
        assert "|" in result.stdout
        assert "cat" in result.stdout


class TestRunSshCmd:
    """Not tested — simple wrapper over run_cmd.

    Testing would require mocks (which we avoid) or a real SSH server.
    The function is straightforward; errors will surface during real usage.
    """
