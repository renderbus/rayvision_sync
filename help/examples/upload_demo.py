# -*- coding: utf-8 -*-
"""Upload demo."""

from rayvision_api import RayvisionAPI
from rayvision_sync.upload import RayvisionUpload

api = RayvisionAPI(access_id="xxxxx",
                   access_key="xxxxx",
                   domain="task.renderbus.com",
                   platform="2")

CONFIG_PATH = [
    r"C:\workspace\work\tips.json",
    r"C:\workspace\work\task.json",
    r"C:\workspace\work\asset.json",
    r"C:\workspace\work\upload.json",
]


UPLOAD = RayvisionUpload(api)
UPLOAD.upload_asset(r"C:\workspace\work\upload.json")
UPLOAD.upload_config("5165465", CONFIG_PATH)
