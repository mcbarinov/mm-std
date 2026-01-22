"""Safe shell command execution with result handling."""

import shlex
import subprocess  # nosec
from dataclasses import dataclass

TIMEOUT_EXIT_CODE = 255
"""Exit code returned when command execution times out."""


@dataclass
class CmdResult:
    """Result of command execution."""

    stdout: str
    stderr: str
    code: int

    @property
    def combined_output(self) -> str:
        """Combined stdout and stderr output."""
        result = ""
        if self.stdout:
            result += self.stdout
        if self.stderr:
            if result:
                result += "\n"
            result += self.stderr
        return result

    @property
    def is_success(self) -> bool:
        """True if command completed successfully (exit code 0)."""
        return self.code == 0

    @property
    def is_timeout(self) -> bool:
        """True if command timed out."""
        return self.code == TIMEOUT_EXIT_CODE


def run_cmd(
    cmd: str, timeout: int | None = 60, capture_output: bool = True, echo_command: bool = False, shell: bool = False
) -> CmdResult:
    """Execute a command.

    Args:
        cmd: Command to execute
        timeout: Timeout in seconds, None for no timeout
        capture_output: Whether to capture stdout/stderr
        echo_command: Whether to print the command before execution
        shell: If False (default), the command is parsed with shlex.split() and
            executed without shell interpretation. Special characters like
            backticks, $(), pipes (|), redirects (>, <), and wildcards (*) are
            treated as literal text. This is the safe mode for commands with
            user input.
            If True, the command is passed to the shell as-is, enabling pipes,
            redirects, command substitution, and other shell features. Use this
            only for trusted commands that need shell functionality.

    Returns:
        CmdResult with stdout, stderr and exit code

    """
    if echo_command:
        print(cmd)  # noqa: T201 - print is intentional for echo_command feature
    try:
        if shell:
            process = subprocess.run(  # noqa: S602 # nosec - shell=True required for pipe support
                cmd, timeout=timeout, capture_output=capture_output, shell=True, check=False
            )
        else:
            process = subprocess.run(  # noqa: S603 # nosec - subprocess with shell=False is safe
                shlex.split(cmd), timeout=timeout, capture_output=capture_output, shell=False, check=False
            )
        stdout = process.stdout.decode("utf-8", errors="replace") if capture_output else ""
        stderr = process.stderr.decode("utf-8", errors="replace") if capture_output else ""
        return CmdResult(stdout=stdout, stderr=stderr, code=process.returncode)
    except subprocess.TimeoutExpired:
        return CmdResult(stdout="", stderr="timeout", code=TIMEOUT_EXIT_CODE)


def run_ssh_cmd(
    host: str,
    cmd: str,
    ssh_key_path: str | None = None,
    timeout: int = 60,
    echo_command: bool = False,
    strict_host_key_checking: bool | None = None,
) -> CmdResult:
    """Execute a command on remote host via SSH.

    Args:
        host: Remote host to connect to
        cmd: Command to execute on remote host
        ssh_key_path: Path to SSH private key file
        timeout: Timeout in seconds
        echo_command: Whether to print the command before execution
        strict_host_key_checking: If True/False, explicitly set StrictHostKeyChecking.
            If None, leave SSH defaults unchanged.

    Returns:
        CmdResult with stdout, stderr and exit code

    """
    ssh_cmd = "ssh -o 'LogLevel=ERROR'"
    if strict_host_key_checking is not None:
        option_value = "yes" if strict_host_key_checking else "no"
        ssh_cmd += f" -o 'StrictHostKeyChecking={option_value}'"
    if ssh_key_path:
        ssh_cmd += f" -i {shlex.quote(ssh_key_path)}"
    ssh_cmd += f" {shlex.quote(host)} {shlex.quote(cmd)}"
    return run_cmd(ssh_cmd, timeout=timeout, echo_command=echo_command)
