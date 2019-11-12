.. note::
   为了更好的体验本API，请查看是否阅读的是最新版的文档。

初窥 rayvision_sync
===================

**rayvision_sync** 是基于Python制作,集合了上传,下载,传输功能的模组,


Sync演示Demo
--------------

学习的最好方法就是参考例子， `rayvision_sync <https://pip.renderbus.com/simple/rayvision-sync/>`_  也不例外，我们也提供了下面的一个使用 **demo** 样例供您把玩学习::

    from rayvision_api import RayvisionAPI
    from rayvision_sync.download import RayvisionDownload
    from rayvision_sync.manage import RayvisionManageTask
    from rayvision_sync.transfer import RayvisionTransfer


    user_info = {
        "domain_name": "task.renderbus.com",
        "platform": "2",
        "access_id": "K2lbvJSlPScStv72niHGXZtbQYc5F6hkj",
        "access_key": "6b4b6eab841772113113b61c79db68d85",
        "local_os": 'windows',
        "workspace": "c:/workspace",
    }

    api = RayvisionAPI(access_id=user_info['access_id'],
                       access_key=user_info['access_key'],
                       domain=user_info['domain_name'],
                       platform=user_info['platform'])


    # Upload json file
    transfer_info = {
        'config_bid': api.user_info['config_bid'],
        'input_bid': api.user_info['input_bid'],
        "domain_name": user_info['domain_name'],
        "platform": user_info['platform'],
        "local_os": user_info['local_os'],
        "user_id": api.user_info['user_id']
    }

    TRANS = RayvisionTransfer(transfer_info)
    manage_task = RayvisionManageTask(api)
    TRANS.manage_task = manage_task
    TRANS.user_info["output_bid"] = api.user_info["output_bid"]
    TRANS.user_info["local_path"] = r"C:\workspace"
    download = RayvisionDownload(TRANS)
    download.auto_download_after_task_completed(["9362074"])

Demo参数:
-----------

.. list-table:: user_info
   :widths: 15 10 50
   :header-rows: 1

   * - 参数名
     - 参数值
     - 描述
   * - domain_name
     - task.renderbus.com
     - 渲染接口URL
   * - platform
     - 2
     - 平台号ID值
   * - access_id
     - K2lbvJSlPScStv72niHGXZtbQYc5F687
     - 用户开发者中心AccessID（非user_id）
   * - access_key
     - 6b4b6eab841772113113b61c79db6899
     - 用户开发者中心AccessKey
   * - local_os
     - windows
     - 用户使用系统（window / linux）
   * - workspace
     - c:/workspace
     - 本地文档保存目录（下载目录可自行设置）

