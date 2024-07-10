# coding=utf-8
"""Download models.

Including download, automatic download (the task is fully rendered,
one frame is downloaded after downloading one frame), download so
the un-downloaded task is recorded (the task is rendered).

"""

import os
# Import built-in modules
import time
import logging

from copy import deepcopy

from rayvision_sync.manage import RayvisionManageTask
# Import local modules
from rayvision_sync.transfer import RayvisionTransfer
from rayvision_sync.exception import DownloadFailed, UnsupportedEngineType
from rayvision_sync.utils import create_transfer_params
from rayvision_sync.utils import run_cmd
from rayvision_sync.utils import str2unicode, get_share_info
from rayvision_log import init_logger
from rayvision_sync.constants import PACKAGE_NAME
from rayvision_sync.rayvision_raysync.transfer_raysync import RayvisionTransferRaysync

class RayvisionDownload(object):
    """Downloader.

    Download all the passed tasks by calling the cmd command.

    """

    def __init__(self, api,
                 transports_json="",
                 transmitter_exe="",
                 automatic_line=True,
                 internet_provider="",
                 logger=None,
                 log_folder=None,
                 log_name=None,
                 log_level="DEBUG",
                 ):
        """Initialize instance.

        Args:
            api (object): rayvision api object.
            transports_json (string): Customize the absolute path of the transfer configuration file.
            transmitter_exe (string): Customize the absolute path of the transfer execution file.
            automatic_line (bool): Whether to automatically obtain the transmission line, the default is "True"
            internet_provider (string): Network provider.
            logger (object): Customize log object.
            log_folder (string): Customize the absolute path of the folder where logs are stored.
            log_name (string): Custom log file name, the system user name will be searched by default.
            log_level (string):  Set log level, example: "DEBUG","INFO","WARNING","ERROR"
        """
        params = create_transfer_params(api)
        params["transports_json"] = transports_json
        params["transmitter_exe"] = transmitter_exe
        params["automatic_line"] = automatic_line
        params["internet_provider"] = internet_provider
        self.api = api
        self.trans = RayvisionTransfer(api, **params)
        self.manage_task = self.trans.manage_task or RayvisionManageTask(api.query)
        self.logger = logger
        if not self.logger:
            init_logger(PACKAGE_NAME, log_folder, log_name)
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(level=log_level.upper())
        self.raysync_engine = RayvisionTransferRaysync(self.api.user_info.get("domain"), self.trans.user_id, self.api.user_info.get("user_name"),
                                                       self.api.query.get_raysync_user_key().get('raySyncUserKey'),
                                                       self.trans.platform, self.logger, timeout=self.api.connect.timeout)

    def _download_log(self, task_id_list, local_path):
        """Download log Settings.

        Args:
            task_id_list (list): List of tasks ids that need to be downloaded.

        """
        self.logger.info('INPUT:')
        self.logger.info('=' * 20)
        self.logger.info('task_id_list: %s', task_id_list)
        self.logger.info('local_path: %s', local_path)
        self.logger.info('=' * 20)

    def _check_local_path(self, local_path):
        """Check the download path.

        Args:
            local_path (str):  Local path to download.

        Returns:
            str

        """
        if not local_path:
            if self.api.user_info['local_os'] == "windows":
                local_path = os.path.join(os.environ["USERPROFILE"],
                                          "renderfarm_sdk")
            else:
                local_path = os.path.join(os.environ["HOME"], "renderfarm_sdk")
        return local_path

    @staticmethod
    def check_params(task_id_list, custom_server_output_path):
        """Check the parameters.
        
        Task_id_list and custom_server_output_path must have one.
        """
        if not task_id_list and not custom_server_output_path:
            raise Exception("One of the task_id_list and custom_server_output_path"
                            " must exist")

    def download(self, task_id_list=None, max_speed=None, print_log=True, download_filename_format="true",
                 local_path=None, server_path=None, engine_type="aspera", server_ip=None, server_port=None,
                 network_mode=0, proxy_ip=None, proxy_port=None, enable_hash=False, asset=False, download_num=2):
        """Download and update the undownloaded record.

        Args:
            task_id_list (list of int): List of tasks ids that need to be
                downloaded.
            max_speed (str, optional): Download speed limit,
                The unit of ``max_speed`` is KB/S,default value is 1048576
                KB/S, means 1 GB/S.
            print_log (bool, optional): Print log, True: print, False: not
                print.
            download_filename_format: File download local save style,
                "true": tape task ID and scene name,
                "false" : download directly without doing processing.
            local_path (str): Download file locally save path,
                default Window system is "USERPROFILE" environment variable address splicing "renderfarm_sdk",
                Linux system is "HOME" environment variable address splicing "renderfarm_sdk",
            server_path (str or list): The user customizes the file structure to be downloaded from
                the output server, and all file structures are downloaded by default,
                example: "18164087_test/l_layer".
            engine_type (str, optional): set engine type, support "aspera" and "raysyncproxy", Default "aspera".
            server_ip (str, optional): transmit server host,
                if not set, it is obtained from the default transport profile.
            server_port (str, optional): transmit server port,
                if not set, it is obtained from the default transport profile.
            network_mode (int): network mode: 0: auto selected, default;
                                               1: tcp;
                                               2: udp;
            proxy_ip(str): proxy ip, only supports raysyncproxy engine eg:10.14.88.66.
            proxy_port(str): proxy port, only supports raysyncproxy engine eg:5555.
            enable_hash(bool): Enable hash verification.
            asset(bool): Download assets or render images True: render images False: assets default False.
            download_num(int): Maximum number of downloads, default is 2.

        Returns:
            bool: True is success.

        """
        if asset and not local_path:
            local_path = os.path.dirname(server_path)
        self.check_params(task_id_list, server_path)
        local_path = self._check_local_path(local_path)
        self.logger.info("[Rayvision_sync start download .....]")
        self._download_log(task_id_list, local_path)

        self._run_download(task_id_list, local_path, max_speed, print_log,
                           download_filename_format, server_path,
                           engine_type=engine_type, server_ip=server_ip, server_port=server_port,
                           network_mode=network_mode, proxy_ip=proxy_ip, proxy_port=proxy_port,
                           enable_hash=enable_hash, asset=asset, download_num=download_num)
        self.logger.info("[Rayvision_sync end download.....]")
        return True

    def auto_download(self, task_id_list=None, max_speed=None, print_log=False, sleep_time=10,
                      download_filename_format="true", local_path=None, engine_type="aspera", server_ip=None,
                      server_port=None, network_mode=0, is_test_stop=False, proxy_ip=None, proxy_port=None,
                      enable_hash=False, download_num=2):
        """Automatic download (complete one frame download).

        Wait for all downloads to update undownloaded records.

        Args:
            task_id_list (list of int): List of tasks ids that need to be
                downloaded.
            max_speed (str, optional): Download speed limit,
                The unit of 'max_speed' is KB/S,default value is 1048576 KB/S,
                means 1 GB/S.
            print_log (bool, optional): Print log, True: print, False: not
                print.
            sleep_time (int, optional): Sleep time between download,
                unit is second.
            download_filename_format: File download local save style,
                "true": tape task ID and scene name,
                "false" : download directly without doing processing.
            local_path (str): Download file locally save path,
                default Window system is "USERPROFILE" environment variable address splicing "renderfarm_sdk",
                Linux system is "HOME" environment variable address splicing "renderfarm_sdk".
            engine_type (str, optional): set engine type, support "aspera" and "raysyncproxy", Default "aspera".
            server_ip (str, optional): transmit server host,
                if not set, it is obtained from the default transport profile.
            server_port (str, optional): transmit server port,
                if not set, it is obtained from the default transport profile.
            network_mode (int): network mode： 0: auto selected, default,
                                               1:tcp
                                               2:udp
            is_test_stop(bool): Stop after test frame completes.
            proxy_ip(str): proxy ip, only supports raysyncproxy engine eg:10.14.88.66.
            proxy_port(str): proxy port, only supports raysyncproxy engine eg:5555.
            enable_hash(bool): Enable hash verification.
            download_num(int): Maximum number of downloads, default is 2.

        Returns:
            bool: True is success.

        """
        local_path = self._check_local_path(local_path)
        self.logger.info("[Rayvision_sync start auto_download.....]")
        self._download_log(task_id_list, local_path)

        self._auto_download_tool(task_id_list, sleep_time,
                                 max_speed, print_log, local_path,
                                 is_test_stop, download_filename_format,
                                 engine_type=engine_type, server_ip=server_ip, server_port=server_port,
                                 network_mode=network_mode,  proxy_ip=proxy_ip, proxy_port=proxy_port,
                                 enable_hash=enable_hash, download_num=download_num)
        self.logger.info("[Rayvision_sync end auto_download.....]")
        return True

    def _auto_download_tool(self, task_id_list, sleep_time,
                            max_speed, print_log, local_path, is_test_stop,
                            download_filename_format="true",
                            engine_type=None, server_ip=None, server_port=None,
                            network_mode=0, proxy_ip=None, proxy_port=None,enable_hash=False,
                            download_num=2):
        """Automatic download (complete one frame download).

        Args:
            task_id_list(list of int): List of tasks ids that need to be
                downloaded.
            sleep_time(int):  Sleep time between download.
            max_speed(str): Download speed limit.
            print_log(bool): Print log, True: print, False: not print.
            local_path (str): Download file locally save path,
                default Window system is "USERPROFILE" environment variable address splicing "renderfarm_sdk",
                Linux system is "HOME" environment variable address splicing "renderfarm_sdk".
            is_test_stop(bool): Stop after test frame completes.
            download_filename_format(str): File download local save style,
                "true": tape task ID and scene name,
                "false" : download directly without doing processing.
            engine_type (str, optional): set engine type, support "aspera" and "raysyncproxy", Default "aspera".
            server_ip (str, optional): transmit server host,
                if not set, it is obtained from the default transport profile.
            server_port (str, optional): transmit server port,
                if not set, it is obtained from the default transport profile.
            network_mode (int): network mode： 0: auto selected, default;
                                               1: tcp;
                                               2: udp;
            proxy_ip(str): proxy ip, only supports raysyncproxy engine eg:10.14.88.66
            proxy_port(str): proxy port, only supports raysyncproxy engine eg:5555
            enable_hash(bool): Enable hash verification.
            download_num(int): Maximum number of downloads, default is 2.

        """
        download_failed_list = list()
        while True:
            if task_id_list:
                time.sleep(float(sleep_time))
                task_id_list_copy = deepcopy(task_id_list)
                for task_id in task_id_list:
                    download_flag = True
                    is_task_end = self.manage_task.is_task_end(task_id, is_test_stop)
                    try:
                        self._run_download([task_id], local_path, max_speed,
                                           print_log, download_filename_format,
                                           engine_type=engine_type, server_ip=server_ip, server_port=server_port,
                                           network_mode=network_mode, proxy_ip=proxy_ip, proxy_port=proxy_port,
                                           enable_hash=enable_hash, download_num=download_num)
                    except DownloadFailed:
                        download_flag = False

                    if is_task_end is True and download_flag is False:
                        download_failed_list.append(task_id)

                    if is_task_end is True:
                        self.logger.info('The tasks end: %s', task_id)
                        task_id_list_copy.remove(task_id)
                task_id_list = deepcopy(task_id_list_copy)
            else:
                break
        if download_failed_list:
            raise DownloadFailed('Finally tasks download failed: %s' % str(download_failed_list))

    def auto_download_after_task_completed(self, task_id_list=None,
                                           max_speed=None, print_log=True,
                                           sleep_time=10,
                                           download_filename_format="true",
                                           local_path=None,
                                           engine_type="aspera", server_ip=None, server_port=None,
                                           network_mode=0,  is_test_stop=False, proxy_ip=None, proxy_port=None,
                                           enable_hash=False, download_num=2):
        """Auto download after the tasks render completed.

        Args:
            task_id_list(list of int): List of tasks ids that need to be
                downloaded.
            max_speed(str, optional): Download speed limit,
                The unit of 'max_speed' is KB/S,default value is 1048576 KB/S,
                means 1 GB/S.
            print_log(bool, optional): Print log, True: print, False: not
                print.
            sleep_time(int, optional): Sleep time between download,
                unit is second.
            download_filename_format: File download local save style,
                "true": tape task ID and scene name,
                "false" : download directly without doing processing.
            local_path (str): Download file locally save path,
                default Window system is "USERPROFILE" environment variable address splicing "renderfarm_sdk",
                Linux system is "HOME" environment variable address splicing "renderfarm_sdk".
            engine_type (str, optional): set engine type, support "aspera" and "raysyncproxy", Default "aspera".
            server_ip (str, optional): transmit server host,
                if not set, it is obtained from the default transport profile.
            server_port (str, optional): transmit server port,
                if not set, it is obtained from the default transport profile.
            network_mode (int): network mode： 0: auto selected, default;
                                               1: tcp;
                                               2: udp;
            is_test_stop(bool): Stop after test frame completes.
            proxy_ip(str): proxy ip, only supports raysyncproxy engine eg:10.14.88.66
            proxy_port(str): proxy port, only supports raysyncproxy engine eg:5555
            enable_hash(bool): Enable hash verification.
            download_num(int): Maximum number of downloads, default is 2.  
            
        Returns:
            bool: True is success.

        """
        local_path = self._check_local_path(local_path)
        self.logger.info("[Rayvision_sync start"
                         "auto_download_after_task_completed .....]")
        self._download_log(task_id_list, local_path)

        while True:
            if task_id_list:
                time.sleep(float(sleep_time))
                for task_id in task_id_list:
                    is_task_end = self.manage_task.is_task_end(task_id, is_test_stop)

                    if is_task_end is True:
                        time.sleep(float(5))
                        self.logger.info('The tasks end: %s', task_id)
                        self._run_download([task_id], local_path,
                                           max_speed, print_log,
                                           download_filename_format,
                                           engine_type=engine_type, server_ip=server_ip, server_port=server_port,
                                           network_mode=network_mode, proxy_ip=proxy_ip, proxy_port=proxy_port,
                                           enable_hash=enable_hash, download_num=download_num)
                        task_id_list.remove(task_id)
            else:
                break
        self.logger.info("[Rayvision_sync end -- "
                         "auto_download_after_task_completed......]")

        return True

    def _run_download(self, task_id_list, local_path, max_speed=None,
                      print_log=True, download_filename_format="true",
                      server_path=None, engine_type="aspera", server_ip=None, server_port=None,
                      network_mode=0, proxy_ip=None, proxy_port=None, enable_hash=False, asset=False, download_num=2):
        """Execute the cmd command for multitasking download.

        Args:
            task_id_list (list of int): Task id list.
            local_path (str): Download to local path.
            max_speed (str): Maximum transmission speed, default value
                is 1048576 KB/S.
            print_log (bool): Print log, True: print, False: not print.
            download_filename_format: File download local save style,
                "true": tape task ID and scene name,
                "false" : download directly without doing processing.
            server_path (str / list): The user customizes the file structure to be downloaded from
                the output server, and all file structures are downloaded by default,
                example: "18164087_test/l_layer".
            engine_type (str, optional): set engine type, support "aspera" and "raysyncproxy", Default "aspera".
            server_ip (str, optional): transmit server host,
                if not set, it is obtained from the default transport profile.
            server_port (str, optional): transmit server port,
                if not set, it is obtained from the default transport profile.
            network_mode (int): network mode： 0: auto selected, default;
                                               1: tcp;
                                               2: udp;
            proxy_ip(str): proxy ip, only supports raysyncproxy engine eg:10.14.88.66
            proxy_port(str): proxy port, only supports raysyncproxy engine eg:5555
            enable_hash(bool): Enable hash verification.
            asset(bool): Download assets or render images True: render images False: assets default False.
            download_num(int): Maximum number of downloads, default is 2.

        """
        transmit_type = 'download_path'
        local_path = str2unicode(local_path)
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        # The unit of 'max_speed' is KB/S, default value is 1048576 KB/S,
        #  means 1 GB/S.
        max_speed = max_speed if max_speed is not None else "1048576"

        if not server_path:
            task_status_list = self.manage_task.get_task_status(task_id_list)
            output_file_names = (self.manage_task.
                                 output_file_names(task_status_list))
        else:
            if isinstance(server_path, str):
                output_file_names = [{"output_name": server_path, "user_id": self.trans.user_id,
                                      "bid": self.trans.output_bid}]
            elif isinstance(server_path, list):
                isinstance(server_path, list)
                output_file_names = [{"output_name": one_path, "user_id": self.trans.user_id,
                                      "bid": self.trans.output_bid} for one_path in server_path ]
            else:
                raise Exception("custom_server_output_path must a list or str.")

        for output_file_name in output_file_names:
            cmd_params = [transmit_type, local_path, output_file_name["output_name"],
                          max_speed, download_filename_format, 'output_bid']
            main_input_bid, main_user_id = get_share_info(self.api)
            bid = main_input_bid if asset else output_file_name["bid"]
            user_id = main_user_id if asset else output_file_name["user_id"]

            if engine_type == "aspera":
                cmd = self.trans.create_cmd(cmd_params, engine_type=engine_type,
                                            server_ip=server_ip, server_port=server_port, bid=bid,
                                            network_mode=network_mode, main_user_id=user_id)
                transfer_code = run_cmd(cmd, print_log=print_log, logger=self.logger)
                
            elif engine_type == "raysyncproxy":
                transfer_code = self.raysync_engine.start_transfer(**{
                    "server_ip": server_ip if server_ip else self.trans.transport_info['raysyncproxy']['server_ip'],
                    "server_port": server_port if server_port else self.trans.transport_info['raysyncproxy']['server_port'],
                    "local_path": local_path,
                    "server_path": output_file_name["output_name"] if download_filename_format == "true" else output_file_name["output_name"].rstrip('\\/')+'/',
                    "storage_id": bid or self.trans.output_bid,
                    "task_type": "download",
                    "task_id": task_id_list[0],
                    "user_id":  user_id,
                    "max_speed": max_speed,
                    "network_mode": network_mode,
                    "proxy_ip": proxy_ip,
                    "proxy_port": proxy_port,
                    "enable_hash": enable_hash,
                    "trans_storage": "input" if asset else "output",
                    "download_num": download_num
                })
            else:
                msg = "{} is not a supported transport engine, " \
                      "currently only support 'aspera' and 'raysyncproxy'".format(engine_type)
                raise UnsupportedEngineType(msg)

            if transfer_code != 0:
                raise DownloadFailed('%s Download failed' % output_file_name)