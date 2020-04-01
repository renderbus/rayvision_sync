"""Transfer Module.

Execute the cmd command to make the last asset and
download assets.

"""

# Import built-in modules
from __future__ import print_function

import codecs
import json
import logging
import os


class RayvisionTransfer(object):
    """Transfer including upload files and download files."""

    def __init__(self, config_bid, input_bid, domain, platform, local_os,
                 user_id, output_bid=None, manage_task=None):
        """Initialize the configuration of the transfer.

        Args:
            config_bid (str): transport configuration id.
            input_bid (str): storage id.
            output_bid (str): storage id.
            domain (str): domain name, like task.renderbus.com".
            platform (str): platform id, for example: "2".
            local_os (str): system name,  Only support "window" or "linux".
            user_id (str): user accound id.
            manage_task (RayvisionManageTask, optional): Instantiated object
                of the management tasks, If it is just uploading, this
                parameter can not be passed. If it is downloaded, this
                parameter must have.
        """
        self.logger = logging.getLogger(__name__)
        self.config_bid = config_bid
        self.input_bid = input_bid
        self.output_bid = output_bid
        self.domain = domain
        self.platform = platform
        self.local_os = local_os
        self.user_id = user_id
        self.manage_task = manage_task
        self.user_info = {
            'config_bid': self.config_bid,
            'input_bid': self.input_bid,
            'output_bid': self.output_bid,
            'user_id': self.user_id,
            'domain': self.domain,
            'platform': self.platform,
            'local_os': self.local_os,
        }
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.transmitter_exe = self.init_transmitter(current_dir, self.local_os)

        self._transports_json = os.path.join(current_dir, 'transmission',
                                             'transports.json')
        self.transport_info = self.parse_transports_json()

    @staticmethod
    def init_transmitter(current_dir, local_os):
        """Gets the path of the transfer software.

        Args:
            current_dir: transfer base directory.
            local_os: system name, Only support "window" or "linux"

        Returns: transfer software absolute path.

        """
        if local_os == 'windows':
            transmitter_exe = os.path.join(current_dir, 'transmission',
                                           local_os,
                                           'rayvision_transmitter.exe')
        else:
            transmitter_exe = os.path.join(current_dir, 'transmission',
                                           local_os,
                                           'rayvision_transmitter')
        return transmitter_exe

    def parse_transports_json(self, transports_json=None, domain=None,
                              platform=None):
        """Analyze transports.json,obtain transfer server info.

        Extract the transmission configuration information of the
        corresponding platform in transports.json.

        Args:
            transports_json (str, optional): Path to transfer configuration
                files.
            domain (str, optional): Domain name.
            platform (str, optional): Platform number.

        Returns:
            dict: Transfer configuration information
                .e.g:
                    {
                        "engine_type":"aspera",
                        "server_name":"HKCT",
                        "server_ip":"render-client.raysync.cn",
                        "server_port":"10221"
                    }

        """
        if not domain:
            domain = self.domain
        if not transports_json:
            transports_json = self._transports_json
        if 'foxrenderfarm' in domain:
            key_first_half = 'foxrenderfarm'
        else:
            key_first_half = 'renderbus'

        if not platform:
            platform = self.platform
        key_second_half = self._get_key_second_half(platform)

        if key_second_half == 'default':
            key = key_second_half
        else:
            key = '%s_%s' % (key_first_half, key_second_half)

        with codecs.open(transports_json, 'r', 'utf-8') as f_transports:
            transports_info = json.load(f_transports)
        return transports_info[key]

    @staticmethod
    def _get_key_second_half(platform):
        """Get the key corresponding to the platform number.

        Returns:
             key_second_half(str): Representative submits tasks to several
                platforms.

        """
        setting_mappings = {
            '2': 'www2',
            '3': 'www3',
            '6': 'www6',
            '20': 'pic',
            '21': 'gpu',
        }
        return setting_mappings[platform]

    def create_cmd(self, cmd_params, db_ini_path=None):
        """Splice a cmd command.

        Args:
            cmd_params (list): Parameters required by the cmd command.

                Examples::

                    [
                        transmit_type, # Transmission type
                        local_path, # Local file path
                        output_file_name, # File path uploaded to the server
                        max_speed, # Maximum transfer speed of upload
                        'true', # Whether to save the path
                        'output_bid', # Transfer id
                    ]

            db_ini_path (str): Database path.

        Returns:
            str: Cmd command.

        """
        transmit_cmd = ('echo y|"{exePath}" "{engineType}" "{serverName}"'
                        ' "{serverIp}" "{serverPort}" "{download_id}"'
                        ' "{userId}" "{transmit_type}" "{local_path}"'
                        ' "{server_path}" "{maxConnectFailureCount}"'
                        ' "{keep_path}" "{max_speed}" "{database_config_path}"'
                        ' ').format(
                            exePath=self.transmitter_exe,
                            engineType=self.transport_info['engine_type'],
                            serverName=self.transport_info['server_name'],
                            serverIp=self.transport_info['server_ip'],
                            serverPort=self.transport_info['server_port'],
                            download_id=self.user_info[cmd_params[5]],
                            userId=self.user_id,
                            transmit_type=cmd_params[0],
                            local_path=cmd_params[1],
                            server_path=cmd_params[2],
                            maxConnectFailureCount='1',  # default is 1.
                            keep_path=cmd_params[4],
                            max_speed=cmd_params[3],
                            database_config_path=db_ini_path)
        return transmit_cmd
