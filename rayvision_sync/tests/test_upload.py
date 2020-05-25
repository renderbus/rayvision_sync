"""Test the rayvision_sync download functions."""

import os

# pylint: disable=import-error
import pytest
from rayvision_sync.exception import RayvisionError


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


def test_create_db_ini(rayvision_upload, tmpdir):
    """Test create_db_ini, we can get a db file."""
    upload_json_path = str(tmpdir.join("upload.json"))
    rayvision_upload.create_db_ini(upload_json_path)
    assert len(os.listdir(rayvision_upload.db_ini)) > 0
