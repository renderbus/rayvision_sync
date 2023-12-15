# -*- coding: utf-8 -*-
"""Upload demo."""
from rayvision_api import RayvisionAPI
from rayvision_api.utils import append_to_upload
from rayvision_sync.upload import RayvisionUpload
from rayvision_sync.utils import cutting_upload

api = RayvisionAPI(access_id="xxxx",
                   access_key="xxxx",
                   domain="task.renderbus.com",
                   platform="21")

config_list = [
    r"C:\workspace\work\tips.json",
    r"C:\workspace\work\task.json",
    r"C:\workspace\work\asset.json",
    r"C:\workspace\work\upload.json",
]

CONFIG_PATH = {
    "tips_json_path": r"C:\workspace\work\tips.json",
    "task_json_path": r"C:\workspace\work\task.json",
    "asset_json_path": r"C:\workspace\work\asset.json",
    "upload_json_path": r"C:\workspace\work\upload.json",
}

UPLOAD = RayvisionUpload(api)
custom_info_to_upload = [
    r"D:\houdini\CG file\local"
]

# custom_info_to_upload = r"D:\houdini\CG file\katana_file"
# append_to_upload(custom_info_to_upload, r"D:\test\upload.json")
# UPLOAD.upload_asset(upload_json_path=r"D:\myproject\local_internal\upload.txt",
#                     transmit_type="upload_json",
#                     engine_type='aspera',
#                     server_ip="45.251.92.16",
#                     server_port="12121")

# UPLOAD.upload_config(task_id="5165465",
#                      config_file_list=config_list,
#                      server_ip="45.251.92.16",
#                      server_port="12121")


# cut upload according to the number of resources
# upload_pool = cutting_upload(r"D:\test\test_upload\1586250829\upload.json", max_resources_number=800)
# print(upload_pool)


# Multi-thread upload
# UPLOAD.multi_thread_upload(upload_pool, thread_num=20)

# Thread pool upload
# UPLOAD.thread_pool_upload(upload_pool, pool_size=20)
#

upload_method = 2
if upload_method == 1:
#     # step4.1:Json files are uploaded in conjunction with CG resources
    UPLOAD.upload(task_id="41235091",
                  engine_type='aspera',
                  server_ip="45.251.92.16",
                  server_port="12121",
                  task_json_path=r"C:\workspace\work\task.json",
                  tips_json_path=r"C:\workspace\work\tips.json",
                  asset_json_path=r"C:\workspace\work\asset.json",
                  upload_json_path=r"C:\workspace\work\upload.json")
elif upload_method == 2:
    # step4.2:CG resource files and json are uploaded separately
    UPLOAD.upload_asset(upload_json_path=CONFIG_PATH["upload_json_path"], engine_type='')
    # UPLOAD.upload_config(str(41235091), list(CONFIG_PATH.values()))
