"""Test the rayvision_sync download functions."""

# pylint: disable=import-error
import pytest

from rayvision_sync.manage import RayvisionManageTask
from rayvision_sync.exception import DownloadFailed


@pytest.mark.parametrize('task_id_list,max_speed,sleep_time', [
    ([258951, 465400, 4664165], '1024', 0),
    ([111], '10240', 2),
    ([8951, 6144, 4665], '2048', 100)
])
def test_download(rayvision_download, task_id_list, max_speed, sleep_time,
                  expected_result, mocker):
    """Test output_file_names, we can get a expected result."""
    mocker_task_id = mocker.patch.object(RayvisionManageTask,
                                         'get_task_status')
    mocker_task_id.return_value = expected_result
    with pytest.raises(DownloadFailed):
        rayvision_download.download(task_id_list, max_speed, sleep_time)


@pytest.mark.parametrize('task_id_list,max_speed,sleep_time', [
    ([25, 614654, 4664165], '1024', 0),
    ([11], '10240', 12),
    ([8951, 6144, 4665], '2048', 100)
])
def test_auto_download(rayvision_download, task_id_list, max_speed, sleep_time,
                       expected_result, mocker):
    """Test auto_download, we can get a expected result."""
    mocker_task_id = mocker.patch.object(RayvisionManageTask,
                                         'get_task_status')
    mocker_task_id.return_value = expected_result
    with pytest.raises(DownloadFailed):
        rayvision_download.download(task_id_list, max_speed, sleep_time)


@pytest.mark.parametrize('task_id_list,max_speed,sleep_time', [
    ([11], '10240', 20),
    ([8951, 6144, 4665], '2048', 5)
])
def test_auto_download_after_task_completed(rayvision_download, task_id_list,
                                            max_speed, sleep_time,
                                            expected_result, mocker):
    """Test auto_download_after_task_completed, we can get a expected result."""
    mocker_task_id = mocker.patch.object(RayvisionManageTask,
                                         'get_task_status')
    mocker_task_id.return_value = expected_result
    with pytest.raises(DownloadFailed):
        rayvision_download.download(task_id_list, max_speed, sleep_time)