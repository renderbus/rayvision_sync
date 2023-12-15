# -*- coding: utf-8 -*-
"""Transfer Module.

Execute the cmd command to make the last asset and
download assets.

"""

# Import built-in modules
from __future__ import print_function

import codecs
import json
import os
import sys

from rayvision_sync.constants import ENGINE_TYPE, PLATFORM_ALIAS_MAP
from rayvision_sync.exception import UnsupportedEngineType


class RayvisionTransfer(object):
    """Transfer including upload files and download files."""

    def __init__(self, api, config_bid, input_bid, domain, platform, local_os,
                 user_id, automatic_line, output_bid=None, manage_task=None,
                 transports_json="", transmitter_exe="", internet_provider="",
                 ):
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
            internet_provider (str): Network provider.
        """
        self.api = api

        self.config_bid = config_bid
        self.input_bid = input_bid
        self.output_bid = output_bid
        self.domain = domain
        self.platform = platform
        self.local_os = local_os
        self.user_id = user_id
        self.manage_task = manage_task
        self.transports_json = transports_json

        self.user_info = {
            'config_bid': self.config_bid,
            'input_bid': self.input_bid,
            'output_bid': self.output_bid,
            'user_id': self.user_id,
            'domain': self.domain,
            'platform': self.platform,
            'local_os': self.local_os,
        }
        if os.path.exists(transmitter_exe):
            self.transmitter_exe = transmitter_exe
        else:
            self.transmitter_exe = self.init_transmitter()
        if automatic_line:
            self.transport_info = self.parse_service_transfe_line(internet_provider)
        else:
            self.transport_info = self.parse_transports_json(transports_json)

    def init_transmitter(self):
        """Gets the path of the transfer software.

        Args:
            current_dir: transfer base directory.

        Returns: transfer software absolute path.

        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        if self.local_os == 'windows':
            transmitter_exe = os.path.join(current_dir, 'transmission',
                                           'windows',
                                           'rayvision_transmitter.exe')
        else:
            transmitter_exe = os.path.join(current_dir, 'transmission',
                                           "linux",
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
            current_dir = os.path.dirname(os.path.realpath(__file__))
            self.transports_json = os.path.join(current_dir, 'transmission',
                                                 'transports.json')
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

        with codecs.open(self.transports_json, 'r', 'utf-8') as f_transports:
            transports_info = json.load(f_transports)
        return transports_info[key]

    def parse_service_transfe_line(self, internet_provider=None):
        transfer_lines = self.api.transmit.get_transfer_config()
        if not transfer_lines:
            raise EnvironmentError("Unable to obtain transmission line")
        resp_engine_lines = transfer_lines.get("resqEngines")
        data = dict()
        for engine_info in resp_engine_lines:
            resp_line = engine_info["respTaskEngineLines"]
            for line in resp_line:
                if internet_provider:
                    if line["name"] == internet_provider:
                        data.update({
                            engine_info["engineName"].lower(): {
                                "server_name": line["name"],
                                "server_ip": line["server"],
                                "server_port": line["port"],
                            }
                        })
                        break
                else:
                    if line["isDefault"]:
                        data.update({
                            engine_info["engineName"].lower(): {
                                "server_name": line["name"],
                                "server_ip": line["server"],
                                "server_port": line["port"],
                            }
                        })
                        break
        return data

    @staticmethod
    def _get_key_second_half(platform):
        """Get the key corresponding to the platform number.

        Returns:
             key_second_half(str): Representative submits tasks to several
                platforms.

        """
        return PLATFORM_ALIAS_MAP[platform]


    def create_cmd(self, cmd_params, db_ini_path=None, engine_type="aspera", server_ip=None, server_port=None,
                   main_user_id=None, main_input_bid=None, bid=None, network_mode=0):
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
            engine_type (str, optional): set engine type, support "aspera" and "raysyncproxy", Default "aspera".
            server_ip (str, optional): transmit server host,
                if not set, it is obtained from the default transport profile.
            server_port (str, optional): transmit server port,
                if not set, it is obtained from the default transport profile.
            main_user_id (str): Main account user id.
            main_input_bid (str): Main account input bid.
            bid (str): Storage id.
            network_mode (int): network mode： 0: auto selected, default;
                                               1: tcp;
                                               2: udp;

        Returns:
            str: Cmd command.

        """
        if not sys.platform.startswith('win'):
            os.environ["LD_LIBRARY_PATH"] = os.path.dirname(self.transmitter_exe)
            chmod_str = "chmod 777 -R {}/*".format(os.path.dirname(self.transmitter_exe))
            os.system(chmod_str)
        if not bool(engine_type):
            engine_type = "aspera"
        if engine_type not in ENGINE_TYPE:
            msg = "{} is not a supported transport engine, " \
                  "currently only support 'aspera' and 'raysyncproxy'".format(engine_type)
            raise UnsupportedEngineType(msg)
        transmit_cmd = ('echo y|"{exePath}" -E "{engineType}"'
                        ' -H "{serverIp}" -P "{serverPort}" -S "{download_id}"'
                        ' -U "{userId}" -T "{transmit_type}" -L "{local_path}"'
                        ' -R "{server_path}" -r "{maxConnectFailureCount}"'
                        ' -K "{keep_path}" -s "{max_speed}" -C "{database_config_path}" -p {network_mode}'
                        ' ').format(
            exePath=self.transmitter_exe,
            engineType=engine_type,
            serverIp=server_ip if server_ip else self.transport_info[engine_type]['server_ip'],
            serverPort=server_port if server_port else self.transport_info[engine_type]['server_port'],
            download_id=main_input_bid if main_input_bid else bid or self.user_info[cmd_params[5]],
            userId=main_user_id if main_user_id else self.user_id ,
            transmit_type=cmd_params[0],
            local_path=cmd_params[1],
            server_path=cmd_params[2],
            maxConnectFailureCount='2',  # default is 2.
            keep_path=cmd_params[4],
            max_speed=cmd_params[3],
            database_config_path=db_ini_path,
            network_mode=int(network_mode))
        return transmit_cmd
