# -*- coding: utf-8 -*-
"""Download demo."""

# Import local modules
from rayvision_api import RayvisionAPI
from rayvision_sync.download import RayvisionDownload

api = RayvisionAPI(access_id="xxxx",
                   access_key="xxx",
                   domain="task.renderbus.com",
                   platform="6")

download = RayvisionDownload(api)
# download.download(download_filename_format="true", server_path="40112885_muti_layer_test")
# download.auto_download([41372307], download_filename_format="false")
# download.auto_download_after_task_completed([41372307], download_filename_format="true", engine_type="raysync")
