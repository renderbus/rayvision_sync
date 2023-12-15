"""Manage operations after generating tasks."""
from copy import deepcopy

from builtins import str

from rayvision_sync.utils import get_task_status_description

from rayvision_sync.constants import TASK_END_STATUS_CODE_LIST


# pylint: disable=useless-object-inheritance
class RayvisionManageTask(object):
    """Processing asset information for a task."""

    def __init__(self, query):
        """Instantiate API interface."""
        self._query = query

    def is_task_end(self, task_id, is_test_stop):
        """Check if the task rendering ends.

        Args:
            task_id (int): Task id

        Returns:
            bool: True: end of task rendering, False/None: Task rendering is
                not over.

        """
        TASK_END_STATUS_CODE_LIST_CP = deepcopy(TASK_END_STATUS_CODE_LIST)
        if is_test_stop:
            TASK_END_STATUS_CODE_LIST_CP.append("40")
        result = None
        task_status_list = self.get_task_status([task_id])
        task_status_codes = self.find_task_status_codes(task_status_list)
        if task_status_codes:
            for task_status_code in task_status_codes:
                if task_status_code not in TASK_END_STATUS_CODE_LIST_CP:
                    result = False
                    break
            if result is not False:
                result = True

        return result

    def get_task_status(self, task_id_list):
        """Get information about each task in the task id list.

        Call the API interface to get the ``items`` information of each task,
        and process it.

        Args:
            task_id_list (list of int): Task id list.

        Returns:
            list: Information about each task id.
                e.g.:
                    [
                        {
                            "task_id":"111",
                            "task_status_code":"25",
                            "task_status_text":"render_task_status_25",
                            "task_status_description":"Done",
                            "is_opener":"0",
                            "output_file_name":"111_test",
                            "sub_task_status":[]
                        },
                        {
                            "task_id":"222",
                            "task_status_code":"0",
                            "task_status_text":"render_task_status_0",
                            "task_status_description":"Waiting",
                            "is_opener":"1",
                            "output_file_name":None,
                            "sub_task_status":[]
                        },
                    ]

        """
        task_info_list = self._query.task_info(task_id_list).get(
            'items',
            [])
        task_status_list = self.task_info_iterater(task_info_list)
        return task_status_list

    def task_info_iterater(self, task_info_list):
        """Item information for each task, extracted and organized.

        Args:
            task_info_list (list): Some details about the task.
                e.g.:
                    [
                        {
                            "sceneName": "demo_scenc.mb",
                            "id': 6419169,
                            "taskAlias': "2W6419169",
                            "taskStatus': 0,
                            "statusText': "render_task_status_0",
                            "preTaskStatus": None,
                            "preStatusText": None,
                            "totalFrames": 10,
                            "abortFrames": 0,
                            "executingFrames": 0,
                            "doneFrames": 0,
                            "failedFrames": 0,
                            "framesRange": "1-10[1]",
                            "projectName": "Project1",
                            "renderConsume": None,
                            "taskArrears": 0.0,
                            "submitDate": 1563356906040,
                            "startTime": None,
                            "completedDate": None,
                            "renderDuration": 0,
                            "userName": "mxinye12",
                            "producer": ",
                            "taskLevel": 80,
                            "taskUserLevel": 0,
                            "taskLimit": 3,
                            "taskOverTime": 12,
                            "overTimeStop": 28800,
                            "userId": 100093088,
                            "outputFileName": "6419169_demo_scenc",
                            "munuTaskId": "2019071702241",
                            "layerParentId": 0,
                            "cgId": 2000,
                            "userAccountConsume": None,
                            "couponConsume": None,
                            "qyCouponConsume": None,
                            "isOpen": 0,
                            "taskType": "Render",
                            "renderCamera": "perspShape",
                            "cloneParentId": 0,
                            "cloneOriginalId": 0,
                            "shareMainCapital": 0,
                            "taskRam": 64,
                            "respRenderingTaskList": None,
                            "layerName": ",
                            "taskTypeText": "render_major_picture_task",
                            "locationOutput": ",
                            "isDelete": 1,
                            "channel": 4,
                            "remark": "gdgsgsg",
                            "isOverTime": 0,
                            "taskKeyValueVo": {
                                "tiles": None,
                                "allCamera": None,
                                "renderableCamera": None
                            },
                            "waitingCount": None
                        },
                        {}
                    ]

        Returns:
            list: Information about each task id.
                e.g.:
                    [
                        {
                            "userId": "1566",
                            "bid": "15555",
                            "task_id":"111",
                            "task_status_code":"25",
                            "task_status_text":"render_task_status_25",
                            "task_status_description":"Done",
                            "is_opener":"0",
                            "output_file_name":"111_test",
                            "sub_task_status":[]
                        },
                        {
                            "userId": "1566",
                            "bid": "15555",
                            "task_id":"222",
                            "task_status_code":"0",
                            "task_status_text":"render_task_status_0",
                            "task_status_description":"Waiting",
                            "is_opener":"1",
                            "output_file_name":"fasfafe",
                            "sub_task_status":[]
                        },
                    ]

        """
        task_status_list = []
        for task_info in task_info_list:
            task_status_dict = {}

            task_id = task_info.get('id')
            task_status_code = str(task_info.get('taskStatus'))  # e.g. 25.
            # e.g. "render_task_status_25".
            task_status_text = task_info.get('statusText')
            # 0: have not sub_task_status; 1:have sub_task_status.
            is_opener = task_info.get('isOpen')
            # Download directory name.
            output_file_name = task_info.get('outputFileName')
            task_status_description = (
                get_task_status_description(task_status_code))
            sub_task_status = []
            if int(is_opener) == 1:
                task_info_list_new = task_info.get('respRenderingTaskList',
                                                   [])
                sub_task_status = self.task_info_iterater(
                    task_info_list_new)

            task_status_dict['task_id'] = str(task_id)
            task_status_dict['task_status_code'] = str(task_status_code)
            task_status_dict['task_status_text'] = str(task_status_text)
            task_status_dict['task_status_description'] = (
                task_status_description)
            task_status_dict['is_opener'] = str(is_opener)
            task_status_dict['output_file_name'] = output_file_name
            task_status_dict['sub_task_status'] = sub_task_status
            task_status_dict['userId'] = task_info.get('userId')
            task_status_dict['bid'] = task_info.get('bid')

            task_status_list.append(task_status_dict)

        return task_status_list

    def output_file_names(self, task_status_list):
        """Get the name of the output scene to download.

        Args:
            task_status_list (list): Task information list.

        Returns:
            list: Output scene name.
                e.g.:
                    [
                        "output_name": "output_name",
                        "user_id": "454415646",
                        "bid": "1515",
                    ]

        """
        output_file_names = []
        for task_status_dict in task_status_list:
            output_file_name = task_status_dict.get('output_file_name',
                                                    None)
            is_opener = task_status_dict.get('is_opener')
            sub_task_status = task_status_dict.get('sub_task_status', [])
            user_id = task_status_dict.get('userId')
            b_id = task_status_dict.get('bid')

            if int(is_opener) == 1:  # Have sub tasks.
                if sub_task_status:
                    output_file_list_sub = (
                        self.output_file_names(sub_task_status))
                    output_file_names.extend(output_file_list_sub)
            else:
                if output_file_name is not None:
                    output_file_names.append({"output_name": output_file_name, "user_id": user_id, "bid": b_id})

        return output_file_names

    def find_task_status_codes(self, task_status_list):
        """Get the task status code from the task information list.

        Args:
            task_status_list (list): Task information list.
                e.g.:
                    [
                        {
                            "task_id":"111",
                            "task_status_code":"25",
                            "task_status_text":"render_task_status_25",
                            "task_status_description":"Done",
                            "is_opener":"0",
                            "output_file_name":"111_test",
                            "sub_task_status":[]
                        },
                        {
                            "task_id":"222",
                            "task_status_code":"0",
                            "task_status_text":"render_task_status_0",
                            "task_status_description":"Waiting",
                            "is_opener":"1",
                            "output_file_name":None,
                            "sub_task_status":[]
                        },
                    ]

        Returns:
            list: Task status code list.
                e.g.:
                    [
                        "25",
                        "10",
                        "35"
                    ]

        """
        task_status_codes = []
        for task_status_dict in task_status_list:
            task_status_code = task_status_dict.get('task_status_code',
                                                    None)
            is_opener = task_status_dict.get('is_opener')
            sub_task_status = task_status_dict.get('sub_task_status', [])

            if int(is_opener) == 1:  # Have sub tasks.
                if sub_task_status:
                    task_status_code_sub = (
                        self.find_task_status_codes(sub_task_status))
                    task_status_codes.extend(task_status_code_sub)
            else:
                if task_status_code is not None:
                    task_status_codes.append(task_status_code)

        return task_status_codes
