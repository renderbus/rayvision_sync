"""The plugin of the pytest.

The pytest plugin hooks do not need to be imported into any test code, it will
load automatically when running pytest.

References:
    https://docs.pytest.org/en/2.7.3/plugins.html

"""

# pylint: disable=import-error
import pytest
from rayvision_api.connect import Connect
from rayvision_api.operators import Query

from rayvision_sync.download import RayvisionDownload
from rayvision_sync.manage import RayvisionManageTask
from rayvision_sync.transfer import RayvisionTransfer
from rayvision_sync.upload import RayvisionUpload


@pytest.fixture()
def user_trans_info(tmpdir):
    """Get user trans info."""
    return {
        'config_bid': '54252',
        'input_bid': '46456',
        'output_bid': '20214',
        'user_id': '100093088',
        'domain': 'tasks.renderbus.com',
        'platform': '2',
        'local_os': 'windows',
        'local_path': str(tmpdir.join('local_path'))
    }


@pytest.fixture(name='user_info_dict')
def user_info():
    """Get the user's login information."""
    return {
        'domain': 'task.renderbus.com',
        'platform': '2',
        'access_id': 'test_access_id',
        'access_key': 'test_access_key',
        'protocol': 'https'
    }


@pytest.fixture()
def expected_result():
    """Get the expected_result information."""
    return [
        {
            'task_id': '6419169',
            'sub_task_status': [],
            'task_status_description': 'Done(with failed frame)',
            'is_opener': '0',
            'task_status_text': 'render_task_status_0',
            'task_status_code': '30',
            'output_file_name': 'test_info_1'
        },
        {
            'task_id': '647611',
            'sub_task_status': [
                {
                    'task_id': '6416355',
                    'sub_task_status': [],
                    'task_status_description': 'Failed',
                    'is_opener': '1',
                    'task_status_text': 'render_task_status_-2',
                    'task_status_code': '45',
                    'output_file_name': 'test_info_3'
                }
            ],
            'task_status_description': 'Abort',
            'is_opener': '1',
            'task_status_text': 'render_task_status_-1',
            'task_status_code': '35',
            'output_file_name': 'test_info_2'
        }
    ]


@pytest.fixture()
def connect(user_info_dict):
    """Create connect API object."""
    return Query(Connect(**user_info_dict))


@pytest.fixture()
def manage(connect):
    """Create an RayvisionManageTask object."""
    return RayvisionManageTask(connect)


@pytest.fixture()
def rayvision_transfer(user_trans_info, manage):
    """Create an RayvisionTransfer object."""
    return RayvisionTransfer(manage_task=manage, **user_trans_info)


@pytest.fixture()
def rayvision_download(rayvision_transfer):
    """Create an RayvisionDownload object."""
    return RayvisionDownload(rayvision_transfer)


@pytest.fixture()
def rayvision_upload(rayvision_transfer):
    """Create an RayvisionDownload object."""
    return RayvisionUpload(rayvision_transfer)
