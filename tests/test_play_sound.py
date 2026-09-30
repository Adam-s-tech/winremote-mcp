"""Unit tests for PlaySound tool."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError


def _call_tool(**kwargs):
    from winremote.__main__ import PlaySound

    return PlaySound(**kwargs)


class TestPlaySound:
    @patch("subprocess.run")
    def test_play_sound_with_path(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = _call_tool(path="C:\\test.wav")
        assert "Played" in result or "task:" in result

    @patch("subprocess.run")
    def test_play_sound_no_args(self, mock_run):
        with pytest.raises(ToolError, match="provide either"):
            _call_tool()

    @patch("subprocess.run")
    def test_play_sound_none_args(self, mock_run):
        with pytest.raises(ToolError, match="provide either"):
            _call_tool(path=None, url=None)

    @patch("subprocess.run")
    def test_play_sound_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("powershell", 30)
        with pytest.raises(ToolError, match="timed out"):
            _call_tool(path="C:\\test.wav")

    @patch("subprocess.run")
    def test_play_sound_error(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="file not found")
        with pytest.raises(ToolError, match="file not found"):
            _call_tool(path="C:\\nonexistent.wav")

    @patch("winremote.__main__._open_validated_fetch_url")
    @patch("subprocess.run")
    def test_play_sound_with_url(self, mock_run, mock_open):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        response = MagicMock()
        response.read.side_effect = [b"audio", b""]
        response.__enter__.return_value = response
        mock_open.return_value = response
        result = _call_tool(url="https://example.com/test.wav")
        assert "Played" in result

    @patch("subprocess.run")
    def test_play_sound_mp3(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = _call_tool(path="C:\\test.mp3")
        assert "Played" in result or "task:" in result
        # Verify MediaPlayer is used for mp3
        call_args = mock_run.call_args
        cmd = call_args[0][0][-1] if call_args else ""
        assert "MediaPlayer" in str(cmd) or "task:" in result

    def test_play_sound_in_tier3(self):
        from winremote.tiers import TOOL_TIERS

        assert "PlaySound" not in TOOL_TIERS["tier1"]
        assert "PlaySound" in TOOL_TIERS["tier3"]
