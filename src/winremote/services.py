"""Windows service and scheduled task management."""

from __future__ import annotations

import subprocess


def _ps(command: str, timeout: int = 30) -> str:
    """Run a PowerShell command and return output."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = result.stdout
    if result.stderr:
        output += f"\n[STDERR] {result.stderr}"
    if result.returncode != 0:
        output += f"\n[Exit code: {result.returncode}]"
    return output.strip() or "(no output)"


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------


def _ps_escape(s: str) -> str:
    """Escape a string for safe use inside PowerShell single-quoted strings."""
    return s.replace("'", "''")


def service_list(filter_str: str = "") -> str:
    """List Windows services."""
    cmd = "Get-Service"
    if filter_str:
        safe = _ps_escape(filter_str)
        cmd = f'$f = \'{safe}\'; Get-Service | Where-Object {{ $_.DisplayName -like "*$f*" -or $_.Name -like "*$f*" }}'
    cmd += " | Format-Table Name, DisplayName, Status -AutoSize"
    return _ps(cmd)


def service_start(name: str) -> str:
    """Start a Windows service."""
    safe = _ps_escape(name)
    return _ps(f"Start-Service -Name '{safe}' -PassThru | Format-Table Name, Status -AutoSize")


def service_stop(name: str) -> str:
    """Stop a Windows service."""
    safe = _ps_escape(name)
    return _ps(f"Stop-Service -Name '{safe}' -Force -PassThru | Format-Table Name, Status -AutoSize")


# ---------------------------------------------------------------------------
# Scheduled Tasks
# ---------------------------------------------------------------------------


def task_list(filter_str: str = "") -> str:
    """List scheduled tasks."""
    cmd = "Get-ScheduledTask"
    if filter_str:
        safe = _ps_escape(filter_str)
        cmd = f"$f = '{safe}'; Get-ScheduledTask | Where-Object {{ $_.TaskName -like \"*$f*\" }}"
    cmd += " | Format-Table TaskName, State, TaskPath -AutoSize"
    return _ps(cmd)


def task_create(name: str, command: str, schedule: str) -> str:
    """Create a scheduled task using schtasks."""
    safe_name = _ps_escape(name)
    safe_command = _ps_escape(command)
    safe_schedule = _ps_escape(schedule)
    cmd = f"schtasks /Create /TN '{safe_name}' /TR '{safe_command}' /SC '{safe_schedule}' /F"
    return _ps(cmd)


def task_delete(name: str) -> str:
    """Delete a scheduled task."""
    safe = _ps_escape(name)
    return _ps(f"schtasks /Delete /TN '{safe}' /F")


# ---------------------------------------------------------------------------
# Event Log
# ---------------------------------------------------------------------------


def event_log(log_name: str = "System", count: int = 20, level: str = "") -> str:
    """Read Windows Event Log entries."""
    count = min(max(count, 1), 1000)
    safe_log = _ps_escape(log_name)
    cmd = f"Get-WinEvent -LogName '{safe_log}' -MaxEvents {count}"
    if level:
        level_map = {
            "critical": 1,
            "error": 2,
            "warning": 3,
            "information": 4,
            "verbose": 5,
        }
        lvl_num = level_map.get(level.lower())
        if lvl_num:
            cmd = f"Get-WinEvent -FilterHashtable @{{LogName='{safe_log}';Level={lvl_num}}} -MaxEvents {count}"
    cmd += " | Format-Table TimeCreated, Id, LevelDisplayName, Message -AutoSize -Wrap"
    return _ps(cmd, timeout=30)
