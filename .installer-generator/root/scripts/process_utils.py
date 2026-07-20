#!/usr/bin/env python3
"""Bounded subprocess execution with whole-process-tree cleanup."""

from __future__ import annotations

import ctypes
import os
import signal
import subprocess
import time
from typing import Any, Sequence

CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def process_is_alive(pid: int) -> bool:
    """Return whether *pid* is alive without terminating or interrupting it."""
    if pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        except OSError:
            return False
        return True

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
    kernel32.GetExitCodeProcess.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int

    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        # Access denied means the process exists but cannot be queried.
        return ctypes.get_last_error() == 5
    try:
        exit_code = ctypes.c_uint32()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == STILL_ACTIVE
    finally:
        kernel32.CloseHandle(handle)


class _WindowsJob:
    """Kill-on-close Windows Job Object for a spawned process tree."""

    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class _BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class _EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        pass

    _EXTENDED_LIMIT_INFORMATION._fields_ = [
        ("BasicLimitInformation", _BASIC_LIMIT_INFORMATION),
        ("IoInfo", _IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]

    def __init__(self, process: subprocess.Popen[Any]) -> None:
        self._handle: int | None = None
        if os.name != "nt":
            return
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        kernel32.CreateJobObjectW.restype = ctypes.c_void_p
        kernel32.SetInformationJobObject.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        kernel32.SetInformationJobObject.restype = ctypes.c_int
        kernel32.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        kernel32.AssignProcessToJobObject.restype = ctypes.c_int
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_int

        handle = kernel32.CreateJobObjectW(None, None)
        if not handle:
            return
        info = self._EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = self.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel32.SetInformationJobObject(
            handle,
            self.JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(info),
            ctypes.sizeof(info),
        ):
            kernel32.CloseHandle(handle)
            return
        process_handle = getattr(process, "_handle", None)
        if process_handle is None or not kernel32.AssignProcessToJobObject(handle, process_handle):
            kernel32.CloseHandle(handle)
            return
        self._handle = int(handle)

    @property
    def active(self) -> bool:
        return self._handle is not None

    def close(self) -> None:
        """Close the job, terminating every process still assigned to it."""
        if self._handle is None:
            return
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_int
        kernel32.CloseHandle(self._handle)
        self._handle = None


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _terminate_process_tree(
    process: subprocess.Popen[Any],
    windows_job: _WindowsJob | None = None,
) -> None:
    """Terminate the entire process tree even when the direct child already exited."""
    if os.name == "nt":
        if windows_job is not None and windows_job.active:
            windows_job.close()
        else:
            # Best-effort fallback for hosts where nested Job Objects are unavailable.
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                    timeout=10,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
            try:
                process.kill()
            except OSError:
                pass
        return

    pgid = process.pid
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError:
        try:
            process.terminate()
        except OSError:
            return

    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        if not _group_exists(pgid):
            return
        time.sleep(0.05)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except OSError:
        try:
            process.kill()
        except OSError:
            pass


def run_bounded(
    command: Sequence[str | os.PathLike[str]],
    *,
    timeout: int | float,
    check: bool = False,
    text: bool = False,
    capture_output: bool = False,
    env: dict[str, str] | None = None,
    cwd: str | os.PathLike[str] | None = None,
    stdin: int | None = None,
) -> subprocess.CompletedProcess[Any]:
    """Run a command with a hard timeout and whole-process-tree ownership."""
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")
    normalized = [os.fspath(part) for part in command]
    if not normalized:
        raise ValueError("command cannot be empty")

    popen_kwargs: dict[str, Any] = {
        "text": text,
        "env": env,
        "cwd": os.fspath(cwd) if cwd is not None else None,
        "stdin": stdin,
    }
    if capture_output:
        popen_kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.name == "nt":
        popen_kwargs["creationflags"] = CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    process = subprocess.Popen(normalized, **popen_kwargs)
    windows_job = _WindowsJob(process) if os.name == "nt" else None
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        _terminate_process_tree(process, windows_job)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            stdout = stderr = None
        raise subprocess.TimeoutExpired(normalized, timeout, output=stdout, stderr=stderr) from exc
    finally:
        # Closing a Windows job also prevents successful commands from leaking descendants.
        if windows_job is not None and windows_job.active:
            windows_job.close()

    # On POSIX, communicate can return only after inherited captured pipes close. For
    # non-captured commands, explicitly reap any descendants still in the session.
    if os.name != "nt" and not capture_output and _group_exists(process.pid):
        _terminate_process_tree(process)

    result = subprocess.CompletedProcess(normalized, process.returncode, stdout, stderr)
    if check and result.returncode:
        raise subprocess.CalledProcessError(
            result.returncode,
            normalized,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result
