"""Test the rayvision_sync manage functions."""

# pylint: disable=import-error
import pytest

from rayvision_api.operators import QueryOperator


@pytest.fixture()
def task_status_list():
    """Get the task_status_list information."""
    return [
        {
            "task_status_code": "-1",
            "is_opener": "1",
            "output_file_name": "test1",
            "sub_task_status": [
                {
                    "task_status_code": "11",
                    "output_file_name": "test2",
                    "is_opener": "0",
                    "userId": "122223",
                    "bid": "122",
                }
            ],
            "userId": "122223",
            "bid": "122",
        },
        {
            "task_status_code": "10",
            "is_opener": "0",
            "output_file_name": "test3",
            "sub_task_status": [],
            "userId": "122222",
            "bid": "123",
        },
    ]


@pytest.fixture()
def task_info_list():
    """Get the task_info_list information."""
    return [
        {
            "id": 6419169,
            "taskStatus": 30,
            "statusText": "render_task_status_0",
            "isOpen": 0,
            "outputFileName": "test_info_1",
            "userId": "1001",
            "bid": "121"
        },
        {
            "id": 647611,
            "taskStatus": 35,
            "statusText": "render_task_status_-1",
            "isOpen": 1,
            "outputFileName": "test_info_2",
            "respRenderingTaskList": [
                {
                    "id": 6416355,
                    "taskStatus": 45,
                    "statusText": "render_task_status_-2",
                    "isOpen": 1,
                    "outputFileName": "test_info_3",
                    "userId": "1002",
                    "bid": "122"
                }
            ],
            "userId": "1002",
            "bid": "122"
        }
    ]


def test_find_task_status_codes(manage, task_status_list):
    """Test find_task_status_codes, we can get a expected result."""
    result = manage.find_task_status_codes(task_status_list)
    assert result == ['11', '10']


def test_output_file_names(manage, task_status_list):
    """Test output_file_names, we can get a expected result."""
    result = manage.output_file_names(task_status_list)
    print(111, result)
    assert result == [{"output_name": "test2", "user_id": "122223", "bid": "122"},
                      {"output_name": "test3", "user_id": "122222", "bid": "123"}]


def test_task_info_iterater(manage, task_info_list, expected_result):
    """Test task_info_iterater, we can get a expected result."""
    data = manage.task_info_iterater(task_info_list)
    assert data == expected_result


@pytest.mark.parametrize('task_id', [
    159423,
    597316,
    2164164
])
def test_is_task_end(manage, mocker, task_info_list, task_id, is_test_stop=False):
    """Test is_task_end, we can get a expected result."""
    task_info = {
        'items': task_info_list
    }
    mocker_task_id = mocker.patch.object(QueryOperator, 'task_info')
    mocker_task_id.return_value = task_info
    result = manage.is_task_end(task_id, is_test_stop)
    assert isinstance(result, bool)
