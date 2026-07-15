"""Lifecycle tests: the MCP server must never outlive its transport or parent.

Regression coverage for KumihoIO/kumiho-plugins#25 (orphaned
``python -m kumiho.mcp_server`` processes accumulating on Windows).
The server process is exercised for real via subprocess; each test asserts
one of the three exit paths:

- stdin EOF (transport closed) ends the process cleanly,
- parent death ends the process even when stdin stays open — and even
  when the dead parent's stderr pipe is broken,
- the watchdog kill switch restores today's behavior.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import textwrap
import time

import pytest

pytest.importorskip("mcp", reason="requires the kumiho[mcp] extra")

SERVER_ENV = {
    **os.environ,
    # Fail-fast sentinel endpoint: no live backend is needed to boot the
    # stdio loop, which is all these tests exercise.
    "KUMIHO_SERVER_ENDPOINT": "lifecycle-test.kumiho.invalid:443",
    "KUMIHO_MCP_ORPHAN_WATCHDOG_POLL": "0.2",
    "PYTHONUNBUFFERED": "1",
}

# Wrapper that plays the part of the Windows launcher: spawn the server on
# our stdin and wait for its startup log line (emitted after the watchdog
# arms), so a slow import can never outrun this handshake. Report the PID,
# linger briefly so the test can assert boot health while the parent is
# still alive, then die. Dying also drops the server's stderr pipe — the
# orphan must still exit through a broken-stderr farewell.
_WRAPPER = textwrap.dedent(
    """
    import subprocess, sys, time
    p = subprocess.Popen(
        [sys.executable, "-m", "kumiho.mcp_server"],
        stdin=0,
        stderr=subprocess.PIPE,
    )
    ready = False
    for line in p.stderr:
        if b"Starting Kumiho MCP server" in line:
            ready = True
            break
    print(p.pid if ready else "BOOTFAIL", flush=True)
    time.sleep(0.5)
    """
)


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_dead(pid: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _alive(pid):
            return True
        time.sleep(0.1)
    return not _alive(pid)


def _spawn_orphan(env: dict) -> int:
    """Start the server under a short-lived wrapper; return the server PID.

    The wrapper's stdin is a pipe whose write end this test process keeps
    open, so the orphaned server never sees EOF — only the parent-death
    watchdog can end it.
    """
    read_fd, write_fd = os.pipe()
    try:
        wrapper = subprocess.Popen(
            [sys.executable, "-c", _WRAPPER],
            stdin=read_fd,
            stdout=subprocess.PIPE,
            env=env,
        )
    finally:
        os.close(read_fd)
    line = wrapper.stdout.readline().strip()
    wrapper.stdout.close()
    if not line or line == b"BOOTFAIL":
        wrapper.kill()
        pytest.fail(f"server did not reach its stdio loop (wrapper said {line!r})")
    server_pid = int(line)
    # The wrapper (parent) is still in its post-handshake linger, so the
    # watchdog cannot have fired yet: a dead server here is a boot crash.
    assert _alive(server_pid), "server died right after startup"
    wrapper.wait(timeout=30)
    # Deliberately leak write_fd until process exit: the open write end is
    # what proves the server exited via the watchdog, not via EOF.
    return server_pid


def test_exits_on_stdin_eof():
    proc = subprocess.Popen(
        [sys.executable, "-m", "kumiho.mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        env=SERVER_ENV,
    )
    try:
        proc.stdin.close()
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        pytest.fail("server still alive 30s after stdin EOF")
    assert proc.returncode == 0, f"EOF shutdown exited rc={proc.returncode}"


@pytest.mark.skipif(os.name == "nt", reason="POSIX watchdog mechanics")
def test_exits_when_parent_dies_without_eof():
    server_pid = _spawn_orphan(SERVER_ENV)
    try:
        assert _wait_dead(server_pid, timeout=15), (
            "orphaned server still alive 15s after its parent died"
        )
    finally:
        if _alive(server_pid):
            os.kill(server_pid, signal.SIGKILL)


@pytest.mark.skipif(os.name == "nt", reason="POSIX watchdog mechanics")
def test_watchdog_kill_switch_keeps_orphan_alive():
    env = {**SERVER_ENV, "KUMIHO_MCP_DISABLE_ORPHAN_WATCHDOG": "1"}
    server_pid = _spawn_orphan(env)
    try:
        # Well past the 0.2s poll interval: with the watchdog disabled the
        # orphan must survive, proving the previous test exercised the
        # watchdog rather than an accidental EOF.
        time.sleep(2.5)
        assert _alive(server_pid), "server died despite disabled watchdog"
    finally:
        if _alive(server_pid):
            os.kill(server_pid, signal.SIGKILL)
