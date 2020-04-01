# -*- coding: utf-8 -*-
"""Download demo."""

# Import local modules
from rayvision_api import RayvisionAPI
from rayvision_sync.download import RayvisionDownload


api = RayvisionAPI(access_id="xxx",
                   access_key="xxx",
                   domain="task.renderbus.com",
                   platform="2")

download = RayvisionDownload(api)
# download.download(download_filename_format="true", server_path="18164087_muti_layer_test/l_ayer2")
# download.auto_download([18164087], download_filename_format="false")
# download.auto_download_after_task_completed([18164087], download_filename_format="false")