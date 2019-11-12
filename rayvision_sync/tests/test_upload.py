"""Test the rayvision_sync download functions."""

import codecs
import json
import os

# pylint: disable=import-error
import pytest
from rayvision_utils.exception.exception import RayvisionError
from rayvision_utils.utils import convert_path


def test_upload_config(rayvision_upload, tmpdir):
    """Test upload_config, we can get a expected result."""
    task_id = 10101
    config_file_list = [
        str(tmpdir.join('task.json')),
        str(tmpdir.join('asset.json')),
        str(tmpdir.join('tips.json')),
        str(tmpdir)
    ]
    with pytest.raises(RayvisionError):
        rayvision_upload.upload_config(task_id, config_file_list)


def test_create_db_ini(rayvision_upload):
    """Test create_db_ini, we can get a db file."""
    rayvision_upload.create_db_ini()
    assert len(os.listdir(rayvision_upload.db_ini)) > 0
