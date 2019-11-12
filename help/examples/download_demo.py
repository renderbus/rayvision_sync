"""Download demo."""

# Import local modules
from rayvision_api import RayvisionAPI
from rayvision_sync.download import RayvisionDownload
from rayvision_sync.manage import RayvisionManageTask
from rayvision_sync.transfer import RayvisionTransfer


render_para = {
    "domain": "task.renderbus.com",  # 用戶不需要修改
    "platform": "2",
    "access_id": "xxxx",  # 用户自行修改(必填)
    "access_key": "xxxx",  # 用户自行修改(必填)
    "local_os": 'windows',
    "workspace": "c:/workspace",  # 本地保存根目录自动创建(用户可自行修改,全英文路径)
    "render_software": "Maya",  # CG软件（Maya, Houdini, Katana, Clarisse）
    "software_version": "2018",  # 注意CG版本的形式
    "project_name": "Project1",
    "plugin_config": {  # CG插件，无插件则为{}
        "mtoa": "3.1.2.1"
    }
}

api = RayvisionAPI(access_id=render_para['access_id'],
                   access_key=render_para['access_key'],
                   domain=render_para['domain'],
                   platform=render_para['platform'])


# Upload json file
transfer_info = {
    'config_bid': api.user_info['config_bid'],
    'input_bid': api.user_info['input_bid'],
    "output_bid": api.user_info["output_bid"],
    "domain": render_para['domain'],
    "platform": render_para['platform'],
    "local_os": render_para['local_os'],
    "user_id": api.user_info['user_id'],
    "local_path": r"C:\workspace",
}

TRANS = RayvisionTransfer(**transfer_info)

manage_task = RayvisionManageTask(api)
TRANS.manage_task = manage_task
download = RayvisionDownload(TRANS)
# 假如task_id = “9362074"
task_id = "9362074"
download.auto_download_after_task_completed([int(task_id)])  # 此处接受的是个列表，列表中元素为int类型
