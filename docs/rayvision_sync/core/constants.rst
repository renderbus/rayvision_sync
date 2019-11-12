常量参数
========

.. automodule:: rayvision_sync.constants
   :members:
   :undoc-members:
   :show-inheritance:

包名(PACKAGE_NAME)
.....

``PACKAGE_NAME`` 设定了日志保存的名称和gitlab 进行自动化部署(CD)打包的包名::

    PACKAGE_NAME = 'rayvision_sync

任务执行状态(TASK_STATUS_DESCRIPTION)
.......

设定了任务的执行状态码和对应的中英文描述::

   TASK_STATUS_DESCRIPTION = {
    "0": {
        "0": "等待中",
        "1": "Waiting"
    },
    "5": {
        "0": "渲染中",
        "1": "Rendering"
    },
    "8": {
        "0": "预处理中",
        "1": "Preprocessing"
    },
    "10": {
        "0": "停止",
        "1": "Stop"
    },
    "20": {
        "0": "欠费停止",
        "1": "Arrearage-stop"
    },
    "23": {
        "0": "超时停止",
        "1": "Timeout stop"
    },
    "25": {
        "0": "已完成",
        "1": "Done"
    },
    "30": {
        "0": "已完成(有失败帧)",
        "1": "Done(with failed frame)"
    },
    "35": {
        "0": "放弃",
        "1": "Abort"
    },
    "40": {
        "0": "等待全速渲染",
        "1": "Test done"
    },
    "45": {
        "0": "失败",
        "1": "Failed"
    }
   }

任务结束状态码(TASK_END_STATUS_CODE_LIST)
........................................

设定了任务结束时的状态码::

   TASK_END_STATUS_CODE_LIST = ['10', '20', '23', '25', '30', '35', '45']

请求头(HEADERS)
........

设定请求头初始参数::

   HEADERS = {
    'accessId': '',
    'channel': '4',
    'platform': '',
    'UTCTimestamp': '',
    'nonce': '',
    'signature': '',
    'version': '1.0.0',
    'Content-Type': 'application/json'
   }