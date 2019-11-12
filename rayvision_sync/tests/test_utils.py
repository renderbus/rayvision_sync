# -*- coding: utf-8 -*-
"""Test the rayvision_sync utils functions."""

from builtins import str

# pylint: disable=import-error
import pytest

from rayvision_sync import utils


@pytest.mark.parametrize("handle_str, str_decode", [
    ("mxxx", "utf-8"),
    ("天天", "utf-8"),
    (b"mxxx", "gbk"),
])
def test_str2unicode(handle_str, str_decode):
    """Test we can get a string."""
    result = utils.str2unicode(handle_str, str_decode)
    assert isinstance(result, str)


@pytest.mark.parametrize("flag, returncode, err_messages", [
    (bool(1), 1, ['error', 'debug']),
])
def test_handle_cmd_result(flag, returncode, err_messages):
    """Test process cmd results."""
    result = utils.handle_cmd_result(flag, returncode, err_messages)
    assert isinstance(result, int)


def test_run_cmd():
    """Test run cmd."""
    cmd_str = "dir"
    result = utils.run_cmd(cmd_str)
    assert isinstance(result, int)


@pytest.mark.parametrize("task_status_code,language ", [
    ("0", "1"),
    ("5", "0"),
    ("35", "1"),
])
def test_get_task_status_description(task_status_code, language):
    """Test task status description."""
    result = utils.get_task_status_description(task_status_code, language)
    if task_status_code == "0":
        assert result == "Waiting"
    elif task_status_code == "5":
        assert result == "渲染中"
    else:
        assert result == "Abort"
