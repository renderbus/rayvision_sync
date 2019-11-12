"""Upload models.

Upload the scene's configuration file and asset file.

"""

# Import built-in modules
import configparser
import os
import time

# Import local modules
from rayvision_sync.utils import run_cmd
from rayvision_sync.utils import str2unicode
from rayvision_sync.utils import upload_retry
from rayvision_utils.exception.exception import RayvisionError


class RayvisionUpload(object):
    """Upload files.

    Upload configuration files and asset files.

    """

    def __init__(self, trans):
        """Initialize instance."""
        self.trans = trans
        self.logger = trans.logger
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.db_ini = os.path.join(current_dir, 'db_ini')
        self._db = os.path.join(current_dir, 'db')

    def create_db_ini(self):
        """Create the database configuration file.

        Returns:
            str: Configuration file path.

        """
        if not os.path.exists(self.db_ini):
            os.makedirs(self.db_ini)
        time_temp = int(time.time())
        db_path = os.path.join(self._db, "%s.db" % time_temp)
        config_ini = configparser.ConfigParser()
        config_ini['database'] = {
            "on": "true",
            "platform_id": self.trans.platform,
            "type": "sqlite"
        }
        config_ini['redis'] = {
            "host": "127.0.0.1",
            "port": 6379,
            "password": "",
            "table_index": "",
            "timeout": 5000
        }
        config_ini['sqlite'] = {
            "db_path": db_path,
            "temporary": "false"
        }

        db_ini_path = os.path.join(self.db_ini, "%s.ini" % time_temp)
        with open(db_ini_path, 'w') as configfile:
            config_ini.write(configfile)
        return db_ini_path

    def upload(self, task_id, task_json_path, tips_json_path, asset_json_path,
               upload_json_path, max_speed=None):
        """Run the cmd command to upload the configuration file.

        Args:
            task_id (str, optional): Task id.
            task_json_path (str, optional): task.json file absolute path.
            tips_json_path (str, optional): tips.json file absolute path.
            asset_json_path (str, optional): asset.json file absolute path.
            upload_json_path (str, optional): upload.json file absolute path.
            max_speed (str): Maximum transmission speed, default value
                is 1048576 KB/S.

        Returns:
            bool: True is success, False is failure.

        """
        config_file_list = [
            task_json_path,
            tips_json_path,
            asset_json_path,
            upload_json_path
        ]
        result_config = self.upload_config(task_id, config_file_list,
                                           max_speed)
        if not result_config:
            return False
        result_asset = self.upload_asset(upload_json_path, max_speed)
        if not result_asset:
            return False
        return True

    def upload_config(self, task_id, config_file_list, max_speed=None):
        """Run the cmd command to upload configuration profiles.

        Args:
            task_id (str): Task id.
            config_file_list (list): Configuration file path list.
            max_speed (str): Maximum transmission speed, default value
                is 1048576 KB/S.

        Returns:
            bool: True is success, False is failure.

        """
        transmit_type = "upload_files"
        max_speed = max_speed if max_speed is not None else "1048576"

        for config_path in config_file_list:
            local_path = str2unicode(config_path)

            config_basename = os.path.basename(config_path)
            server_path = '/{0}/cfg/{1}'.format(task_id, config_basename)
            server_path = str2unicode(server_path)

            if not os.path.exists(local_path):
                self.logger.info('%s is not exists.', local_path)
                continue
            cmd_params = [transmit_type, local_path, server_path, max_speed,
                          'false', 'config_bid']
            cmd = self.trans.create_cmd(cmd_params)

            times = 0
            while True:
                result = run_cmd(cmd, flag=True, logger=self.logger)
                if result:
                    if times == 9:
                        raise RayvisionError(20004, "%s upload failed" %
                                             config_path)
                    times += 1
                else:
                    break
        return True

    @upload_retry
    def upload_asset(self, upload_json_path, max_speed=None):
        """Run the cmd command to upload asset files.

        Args:
            upload_json_path (str): Path to the upload.json file.
            max_speed (str): Maximum transmission speed, default value
                is 1048576 KB/S.

        Returns:
            bool: True is success, False is failure.

        """
        transmit_type = "upload_file_pairs"
        max_speed = max_speed if max_speed is not None else "1048576"
        cmd_params = [transmit_type, upload_json_path, '/', max_speed,
                      'false', 'input_bid']
        db_ini_path = self.create_db_ini()
        cmd = self.trans.create_cmd(cmd_params, db_ini_path)

        return run_cmd(cmd, flag=True, logger=self.logger)
