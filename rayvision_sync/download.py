"""Download models.

Including download, automatic download (the task is fully rendered,
one frame is downloaded after downloading one frame), download so
the un-downloaded task is recorded (the task is rendered).

"""

# Import built-in modules
import time
import os

# Import local modules
from rayvision_sync.transfer import RayvisionTransfer
from rayvision_sync.manage import RayvisionManageTask
from rayvision_sync.utils import run_cmd
from rayvision_sync.utils import str2unicode
from rayvision_sync.utils import create_transfer_params


class RayvisionDownload(object):
    """Downloader.

    Download all the passed tasks by calling the cmd command.

    """

    def __init__(self, api):
        """Initialize instance."""
        params = create_transfer_params(api)
        self.api = api
        self.trans = RayvisionTransfer(**params)
        self.manage_task = self.trans.manage_task or RayvisionManageTask(api.query)
        self.logger = self.trans.logger

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

    def download(self, task_id_list=None,
                 max_speed=None, print_log=True,
                 download_filename_format="true",
                 local_path=None, server_path=None):
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

        Returns:
            bool: True is success.

        """
        self.check_params(task_id_list, server_path)
        local_path = self._check_local_path(local_path)
        self.logger.info("[Rayvision_sync start download .....]")
        self._download_log(task_id_list, local_path)

        self._run_download(task_id_list, local_path, max_speed, print_log,
                          download_filename_format, server_path)
        self.logger.info("[Rayvision_sync end download.....]")
        return True

    def auto_download(self, task_id_list=None, max_speed=None,
                      print_log=False, sleep_time=10,
                      download_filename_format="true",
                      local_path=None):
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

        Returns:
            bool: True is success.

        """
        local_path = self._check_local_path(local_path)
        self.logger.info("[Rayvision_sync start auto_download.....]")
        self._download_log(task_id_list, local_path)

        self._auto_download_tool(task_id_list, sleep_time,
                                 max_speed, print_log, local_path,
                                 download_filename_format)
        self.logger.info("[Rayvision_sync end auto_download.....]")
        return True

    def _auto_download_tool(self, task_id_list, sleep_time,
                            max_speed, print_log, local_path,
                            download_filename_format="true"):
        """Automatic download (complete one frame download).

        Args:
            task_id_list(list of int): List of tasks ids that need to be
                downloaded.
            sleep_time(int):  Sleep time between download.
            max_speed(str): Download speed limit.
            print_log(bool): Print log, True: print, False: not print.
            download_filename_format(str): File download local save style,
                "true": tape task ID and scene name,
                "false" : download directly without doing processing.

        """
        while True:
            if task_id_list:
                time.sleep(float(sleep_time))
                for task_id in task_id_list:
                    is_task_end = self.manage_task.is_task_end(task_id)
                    self._run_download([task_id], local_path, max_speed,
                                      print_log, download_filename_format)

                    if is_task_end is True:
                        self.logger.info('The tasks end: %s', task_id)
                        task_id_list.remove(task_id)
            else:
                break

    def auto_download_after_task_completed(self, task_id_list=None,
                                           max_speed=None, print_log=True,
                                           sleep_time=10,
                                           download_filename_format="true",
                                           local_path=None):
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
                    is_task_end = self.manage_task.is_task_end(task_id)

                    if is_task_end is True:
                        time.sleep(float(5))
                        self.logger.info('The tasks end: %s', task_id)
                        self._run_download([task_id], local_path,
                                          max_speed, print_log,
                                          download_filename_format,
                                          )
                        task_id_list.remove(task_id)
            else:
                break
        self.logger.info("[Rayvision_sync end -- "
                         "auto_download_after_task_completed......]")

        return True

    def _run_download(self, task_id_list, local_path, max_speed=None,
                        print_log=True, download_filename_format="true",
                        server_path=None):
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

        """
        transmit_type = 'download_files'
        local_path = str2unicode(local_path)
        # The unit of 'max_speed' is KB/S, default value is 1048576 KB/S,
        #  means 1 GB/S.
        max_speed = max_speed if max_speed is not None else "1048576"

        if not server_path:
            task_status_list = self.manage_task.get_task_status(task_id_list)
            output_file_names = (self.manage_task.
                                 output_file_names(task_status_list))
        else:
            if isinstance(server_path, str):
                output_file_names = [server_path]
            elif isinstance(server_path, list):
                isinstance(server_path, list)
                output_file_names = server_path
            else:
                raise Exception("custom_server_output_path must a list or str.")

        for output_file_name in output_file_names:
            cmd_params = [transmit_type, local_path, output_file_name,
                          max_speed, download_filename_format, 'output_bid']

            cmd = self.trans.create_cmd(cmd_params)
            run_cmd(cmd, print_log=print_log, logger=self.logger)
