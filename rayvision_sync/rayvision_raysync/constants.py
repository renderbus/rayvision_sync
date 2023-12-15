# -*- coding:utf-8 -*-
"""Constant information about the sync."""

PACKAGE_NAME = 'rayvision_raysync'

HEADERS = {
            'Content-Type': 'application/json'
        }

RESPONSE = {
    "ready": 100,
    "start": 101,
    "stopped": 102,
    "successful": 0,
    "failed": 500,
    "auth-failed": 201,
    "proxy-closed": 202,
    "idle": 300,
    "stop-by-server": 301,
    "no-permission": 405,
    "ip-locked": 205,
    "account-locked": 209
}

DOMAIN = "http://127.0.0.1"

# process path
RAYSYNC_NAME = {
    "Windows": "Raysync Client",
    "Linux": "RaysyncCmd",
    "Darwin": "RaysyncMac/RaysyncClientManager.app/Contents/MacOS",
    "Mac": "RaysyncMac",
}

# process name
RAYSYNCEXE = {
    "Windows": "Raysync-sdk.exe",
    "Linux": "Raysync-sdk",
    "Darwin": "Raysync-sdk",
}

STATU_SLEEP = 5