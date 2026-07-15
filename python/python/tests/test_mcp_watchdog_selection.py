"""Unit tests for the Windows watchdog's ancestor-chain selection.

`_select_watch_pids` is pure logic over a pid table, so the Windows
topologies — including the venv redirector-stub chain reported on PR #78
— are testable on any platform. Table shape: pid -> (ppid, exe basename,
lowercase).
"""

from __future__ import annotations

from kumiho.mcp_server import _select_watch_pids

SERVER = 100  # "this process": base python.exe -m kumiho.mcp_server


def test_venv_stub_chain_watches_through_to_client():
    # kaveone's observed real-deployment topology (PR #78 review):
    # client <- launcher-stub <- launcher <- server-stub <- server
    table = {
        SERVER: (90, "python.exe"),
        90: (80, "python.exe"),   # venv Scripts\python.exe redirector stub
        80: (70, "python.exe"),   # run_kumiho_mcp.py launcher (base python)
        70: (60, "python.exe"),   # launcher's own venv stub hop
        60: (50, "claude.exe"),   # the MCP client
        50: (1, "explorer.exe"),  # must NOT be watched
    }
    watch, broken = _select_watch_pids(table, SERVER)
    assert watch == [90, 80, 70, 60]
    assert broken is None


def test_single_stub_hop():
    table = {
        SERVER: (90, "python.exe"),
        90: (60, "python.exe"),   # stub
        60: (50, "node.exe"),     # client
        50: (1, "wt.exe"),
    }
    watch, broken = _select_watch_pids(table, SERVER)
    assert watch == [90, 60]
    assert broken is None


def test_direct_spawn_watches_only_the_client():
    table = {
        SERVER: (60, "python.exe"),
        60: (50, "claude.exe"),
        50: (1, "explorer.exe"),
    }
    watch, broken = _select_watch_pids(table, SERVER)
    assert watch == [60]
    assert broken is None


def test_pythonw_and_py_launcher_count_as_plumbing():
    table = {
        SERVER: (90, "python.exe"),
        90: (80, "pythonw.exe"),
        80: (60, "py.exe"),
        60: (1, "code.exe"),
    }
    watch, broken = _select_watch_pids(table, SERVER)
    assert watch == [90, 80, 60]
    assert broken is None


def test_missing_ancestor_reports_broken_chain():
    # The stub's recorded parent is gone: chain already broken mid-import.
    table = {
        SERVER: (90, "python.exe"),
        90: (80, "python.exe"),
        # 80 vanished
    }
    watch, broken = _select_watch_pids(table, SERVER)
    assert watch == [90]
    assert broken == 80


def test_missing_direct_parent_reports_broken_chain():
    table = {SERVER: (90, "python.exe")}
    watch, broken = _select_watch_pids(table, SERVER)
    assert watch == []
    assert broken == 90


def test_ppid_cycle_stops_cleanly():
    # PID recycling can fabricate cycles in the snapshot; never loop.
    table = {
        SERVER: (90, "python.exe"),
        90: (SERVER, "python.exe"),
    }
    watch, broken = _select_watch_pids(table, SERVER)
    assert watch == [90]
    assert broken is None


def test_depth_cap_bounds_pathological_chains():
    table = {SERVER: (101, "python.exe")}
    for pid in range(101, 120):
        table[pid] = (pid + 1, "python.exe")
    table[120] = (1, "python.exe")
    watch, broken = _select_watch_pids(table, SERVER, max_depth=6)
    assert len(watch) == 6
    assert broken is None


def test_pid_zero_parent_stops():
    # System Idle Process parent (pid 0) is not a real ancestor.
    table = {SERVER: (0, "python.exe")}
    watch, broken = _select_watch_pids(table, SERVER)
    assert watch == []
    assert broken is None


def test_own_pid_missing_from_table():
    watch, broken = _select_watch_pids({}, SERVER)
    assert watch == []
    assert broken is None
