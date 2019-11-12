"""Download models.

Including download, automatic download (the task is fully rendered,
one frame is downloaded after downloading one frame), download so
the un-downloaded task is recorded (the task is rendered).

"""

# Import built-in modules
import time

# Import local modules
from rayvision_sync.utils import run_cmd
from rayvision_sync.utils import str2unicode


class RayvisionDownload(object):
    """Downloader.

    Download all the passed tasks by calling the cmd command.

    """

    def __init__(self, trans):
        """Initialize instance."""
        self.trans = trans
        self.manage_task = trans.manage_task
        self.logger = trans.logger
        self.local_path = trans.user_info["local_path"]

    def _download_log(self, task_id_list):
        """Download log Settings.

        Args:
            task_id_list (list): List of tasks ids that need to be downloaded.

        """
        self.logger.info('INPUT:')
        self.logger.info('=' * 20)
        self.logger.info('task_id_list: %s', task_id_list)
        self.logger.info('local_path: %s', self.local_path)
        self.logger.info('=' * 20)

    def download(self, task_id_list,
                 max_speed=None, print_log=True):
        """Download and update the undownloaded record.

        Args:
            task_id_list (list of int): List of tasks ids that need to be
                downloaded.
            max_speed (str, optional): Download speed limit,
                The unit of ``max_speed`` is KB/S,default value is 1048576
                KB/S, means 1 GB/S.
            print_log (bool, optional): Print log, True: print, False: not
                print.

        Returns:
            bool: True is success.

        """
        self.logger.info("[Rayvision_sync start download .....]")
        self._download_log(task_id_list)

        self.run_download(task_id_list, self.local_path, max_speed, print_log)
        self.logger.info("[Rayvision_sync end download.....]")
        return True

    def auto_download(self, task_id_list, max_speed=None,
                      print_log=False, sleep_time=10):
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

        Returns:
            bool: True is success.

        """
        self.logger.info("[Rayvision_sync start auto_download.....]")
        self._download_log(task_id_list)

        self._auto_download_tool(task_id_list, sleep_time,
                                 max_speed, print_log)
        self.logger.info("[Rayvision_sync end auto_download.....]")
        return True

    def _auto_download_tool(self, task_id_list, sleep_time,
                            max_speed, print_log):
        """Automatic download (complete one frame download).

        Args:
            task_id_list(list of int): List of tasks ids that need to be
                downloaded.
            sleep_time(int):  Sleep time between download.
            max_speed(str): Download speed limit.
            print_log(bool): Print log, True: print, False: not print.

        """
        while True:
            if task_id_list:
                time.sleep(float(sleep_time))
                for task_id in task_id_list:
                    is_task_end = self.manage_task.is_task_end(task_id)
                    self.run_download([task_id], self.local_path, max_speed,
                                      print_log)

                    if is_task_end is True:
                        self.logger.info('The tasks end: %s', task_id)
                        task_id_list.remove(task_id)
            else:
                break

    def auto_download_after_task_completed(self, task_id_list,
                                           max_speed=None, print_log=True,
                                           sleep_time=10):
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

        Returns:
            bool: True is success.

        """
        self.logger.info("[Rayvision_sync start"
                         "auto_download_after_task_completed .....]")
        self._download_log(task_id_list)

        while True:
            if task_id_list:
                time.sleep(float(sleep_time))
                for task_id in task_id_list:
                    is_task_end = self.manage_task.is_task_end(task_id)

                    if is_task_end is True:
                        time.sleep(float(5))
                        self.logger.info('The tasks end: %s', task_id)
                        self.run_download([task_id], self.local_path,
                                          max_speed, print_log)
                        task_id_list.remove(task_id)
            else:
                break
        self.logger.info("[Rayvision_sync end -- "
                         "auto_download_after_task_completed......]")

        return True

    def run_download(self, task_id_list, local_path, max_speed=None,
                     print_log=True):
        """Execute the cmd command for multitasking download.

        Args:
            task_id_list (list of int): Task id list.
            local_path (str): Download to local path.
            max_speed (str): Maximum transmission speed, default value
                is 1048576 KB/S.
            print_log (bool): Print log, True: print, False: not print.

        """
        transmit_type = 'download_files'
        local_path = str2unicode(local_path)
        # The unit of 'max_speed' is KB/S, default value is 1048576 KB/S,
        #  means 1 GB/S.
        max_speed = max_speed if max_speed is not None else "1048576"

        task_status_list = self.manage_task.get_task_status(task_id_list)
        output_file_names = (self.manage_task.
                             output_file_names(task_status_list))

        for output_file_name in output_file_names:
            cmd_params = [transmit_type, local_path, output_file_name,
                          max_speed, 'true', 'output_bid']

            cmd = self.trans.create_cmd(cmd_params)
            run_cmd(cmd, print_log=print_log, logger=self.logger)
