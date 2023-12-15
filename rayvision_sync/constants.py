# -*- coding:utf-8 -*-
"""Constant information about the sync."""

PACKAGE_NAME = 'rayvision_sync'

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

TASK_END_STATUS_CODE_LIST = ['10', '20', '23', '25', '30', '35', '45']

TRANSFER_LOG = "RAYVISION_LOG"
RAYVISION_DB = "RAYVISION_DB"

WINDOWS_LOCAL_ENV = "USERPROFILE"
LINUX_LOCAL_ENV = "HOME"
RENDERFARM_SDK = "renderfarm_sdk"

ENGINE_TYPE = ['aspera', 'raysyncproxy']

PLATFORM_ALIAS_MAP = {
            '2': 'www2',
            '3': 'www3',
            '6': 'www6',
            '20': 'pic',
            '21': 'gpu',
            '35': 'gpu5',
        }