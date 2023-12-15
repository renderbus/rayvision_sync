import time
import requests
import os
import json
import codecs
import subprocess
import zipfile
import platform as plm
from pprint import pformat
from tqdm.auto import tqdm
from xml.etree.ElementTree import parse
from rayvision_sync.rayvision_raysync.url import ApiUrl
from rayvision_sync.rayvision_raysync.constants import RAYSYNC_NAME, RAYSYNCEXE, HEADERS, DOMAIN, RESPONSE, STATU_SLEEP
from rayvision_sync.rayvision_raysync.exception import TaskidNotexsit, DownloadRaysyncFailed, RaysyncAPIError, \
    NotfoundRaysyncInI, NotSupportfiletype, CreatTaskFailed, TransferTimeout, LaunchRaysyncfailed, NotSupportTasktype


class RayvisionTransferRaysync():
    ''' Interactive Raysync interface '''

    def __init__(self, task_domain, user_id, user_name, user_key, platform, logger=None, raysyncdirpath=None):
        """
        _headers: The generic interface request header for Raysync;
        _domain: The generic interface request IP for Raysync;
        _raysyncdirpath: Directory where the Raysync resides;
        _raysyncexe: Raysync EXE Execution file;
        _baseUrl: The generic interface request URL for Raysync;
        _url: A set of interfaces for a Raysync service
        _port: The generic interface service port for Raysync;
        :param task_domain: eg:task.renderbus.com
        :param user_id: eg:1000001
        :param user_name: RD_example
        :param platform: Platform number
        :param logger: The log object
        :param raysyncdirpath: Path where the Raysync resides
        """
        self.logger = logger
        self._headers = HEADERS
        self._domain = DOMAIN
        self._resultDict = RESPONSE
        self._system = plm.system()
        self._base_url = None
        self._raysyncdirpath = raysyncdirpath if raysyncdirpath else os.path.join(
            os.path.dirname(__file__), RAYSYNC_NAME[self._system])
        self._raysyncexe = os.path.join(
            self._raysyncdirpath, RAYSYNCEXE[self._system])
        self._url = ApiUrl
        self._task_failed_dict = {}
        self.password = "%s&1&%s&12345678" % (user_key, platform)
        self.task_domain = task_domain
        self.user_id = user_id
        self.user_name = user_name
        self.service_statu = False

    def auto_download(self):
        """The static raysync package is automatically downloaded"""
        try:
            if os.path.exists(self._raysyncexe):
                self.logger.debug('Raysyncweb is detected!')
                return
            self.logger.debug(
                'No Raysyncweb is detected. Prepare to download the latest Raysyncweb automatically!')
            raysync_name = RAYSYNC_NAME[self._system.replace("Darwin", 'Mac')] + '.zip'
            raysync_link = "https://{}/download/{}".format(
                self.task_domain, raysync_name)
            zip_path = os.path.join(
                os.path.dirname(__file__), raysync_name)
            response = requests.get(raysync_link, stream=True)
            total = int(response.headers.get('content-length', 0))
            self.logger.debug(zip_path)
            with open(zip_path, 'wb') as file, tqdm(
                    desc=os.path.basename(zip_path),
                    total=total,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                    ncols=100
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    bar.update(len(data))
            self.logger.debug('Raysyncweb download success!')
            with zipfile.ZipFile(zip_path, "r") as zip_obj:
                zip_obj.extractall(path=os.path.dirname(__file__))
        except:
            raise DownloadRaysyncFailed("Raysyncweb download failure!")

    def post(self, api_url, data):
        """Create a common request mode
            :param api_url: request api eg: /create-task
            :param data: reuqest parameter
            eg: {
                "task-name": "upload-test",
                "server-ip": "192.168.1.1",
                "server-port": 2442,
                "server-ssl-port": 2443,
                "proxy-port": 32001,
                "protocol-type": "auto",
                "delay-threshold": 10,
                "account": "test",
                "password": "123456",
                "group-id": 0,
                "task-type": "upload",
                "source-path": "/root/test",
                "target-path": "/",
                "enable-ssl":false,
                "enable-hash":false
                }
            :return {"code":0, "message": "success"}
        """
        request_address = self._base_url + api_url
        if api_url not in [self._url.start_task, self._url.get_task_status,
                           self._url.set_transfer_speed]:
            # start_task|get_task_status not print!
            self.logger.debug('POST: %s', request_address)
            self.logger.debug('HTTP Headers: %s',
                              pformat(self._headers, width=500))
            self.logger.debug('HTTP Body: %s', pformat(data, width=500))
        response = requests.post(
            request_address, json=data, headers=self._headers, proxies={"http": self._base_url})
        json_response = response.json()
        self.logger.debug('HTTP Response: %s', json_response)
        code = json_response["code"]
        if code != 0:
            raise RaysyncAPIError(code, json_response['message'], response.url)
        return json_response

    @property
    def _port(self):
        '''
            Read the listening port from the configuration file
            Raysync Client/cluster.xml is Port Configuration File, read port info
        '''
        xml_path = os.path.join(self._raysyncdirpath, 'cluster.xml')
        if not os.path.exists(xml_path):
            raise NotfoundRaysyncInI(
                'Port profile cluster.xml not found, Raysync engine package incomplete！')
        tree = parse(xml_path)
        root = tree.getroot()
        port = root[0][0].attrib['value']
        return port

    def set_transfer_speed(self, max_speed, network_mode=0):
        """Setting the transmission speed"""
        max_speed = max_speed if max_speed is not None else "1048576"
        params = {
            "max-upload-speed": int(max_speed),
            "max-download-speed": int(max_speed)
        }
        if network_mode != 1:
            params["mss"] = 1200
        self.post(self._url.set_transfer_speed, params)
        self.logger.info("The current maximum download speed is %s KB/S, "
                         "The current maximum upload speed is %s KB/S!"
                         % (int(max_speed), int(max_speed)))

    def set_proxy_manager(self, proxy_ip, proxy_port):
        """Setting the transmission speed"""
        enable_proxy = True if proxy_ip and proxy_port else False
        proxy_ip = proxy_ip if enable_proxy else ""
        proxy_port = int(proxy_port) if enable_proxy else 0
        params = {
            "enable-proxy-manager": enable_proxy,
            "proxy-manager-ip": proxy_ip,
            "proxy-manager-port": proxy_port
        }
        self.post(self._url.set_proxy_manager, params)
        self.logger.info("set Proxy enable:%s %s:%s" % (enable_proxy, proxy_ip, proxy_port))

    def get_run_raysync(self):
        """Get the command to start the program of Raysync."""
        if self._system == "Windows":
            run_raysync_cmd = self._raysyncexe
        elif self._system == "Linux":
            run_raysync_cmd = "sh \"%s\"" % os.path.join(self._raysyncdirpath, "start.sh")
        else:
            run_raysync_cmd = '\"%s\" --localConfig' % self._raysyncexe
        return run_raysync_cmd

    def listening_raysync_server(self):
        """Listening to the Raysync."""
        try:
            self._base_url = "%s:%s" % (self._domain, self._port)
            if not self.service_statu:
                self.close_raysync()
                self.logger.info(
                    'Start the Raysync-man.exe to listen for the process(port=%s)....' % self._port)
                run_raysync_cmd = self.get_run_raysync()
                self.raysync_app = subprocess.Popen(run_raysync_cmd, shell=True)
                result_code = True
                while result_code:
                    try:
                        url = self._base_url + self._url.check_raysync_http
                        response = requests.post(url, headers=self._headers, json={"sign": "render-bus"},
                                                 proxies={"http": self._base_url}).json()
                        result_code = response.get('code')
                    except:
                        time.sleep(0.2)
                        pass
                self.logger.info('Raysync-man server has started successfully')
                self.service_statu = True
            return True
        except:
            raise LaunchRaysyncfailed(
                "Description Failed to start the Raysync client!")

    def close_raysync(self):
        """close the Raysync service"""
        if self._system == "Windows":
            os.system('taskkill /f /im "%s"' % (RAYSYNCEXE[self._system]))
        elif self._system == "Linux":
            os.system("sh \"%s\"" % os.path.join(self._raysyncdirpath, "stop.sh"))
        else:
            os.system("pkill %s" % (RAYSYNCEXE[self._system]))

    def convert_upload(self, upload_path, input_id):
        """ create upload_list.json """
        upload_json_data = json.load(codecs.open(
            upload_path, "r", encoding="utf-8"))
        asset_list = upload_json_data.get('asset')
        upload_list_name = os.path.splitext(os.path.basename(upload_path))[0]
        upload_list_file = os.path.join(os.path.dirname(upload_path), "%s_list.json" % upload_list_name)
        with codecs.open(upload_list_file, "w", encoding="utf-8") as f_upload_list_file:
            for item in asset_list:
                server = "/input/%s-%s" % (input_id, self.user_id) + item["server"]
                f_upload_list_file.write('local:"%s" server:"%s"\n' % (item["local"], server))
        return upload_list_file

    def get_transfer_path(self, task_type, local_path, server_path, storage_id, task_id, file_type, downstorage,
                          user_id=None):
        """ Concatenate server paths based on transmission paths
        @:param: task_type
                eg:uoload(normal): {
                    "source_path": "%appdata%/renderfam_sdk/file.max"
                    "target_path": "/input/config_id-user_id"
                }
                uoload(config_file): {
                    "source_path": "%appdata%/renderfam_sdk/task.json"
                    "target_path": "/input/config_id-user_id/task_id/cfg"
                }
                upload-list: {
                    "file-list": "F:\\Project\\SDK\\upload_list.json",
                }
                download: {
                    "source-path": r'/output/config_id-user_id/server_path',
                    "target-path": r'C:/Users/chenshengzhen/renderfarm_sdk',  #只接收目录
                }
        @:param: file_type: {
                    "normal": transfer normal files,
                    "josn": transfer task.json, asset.json, upload.json files,
                }
        :return: source_dict = {source_path = "", target_path = ""}
        """
        path_dict = {
            "task-type": task_type
        }
        server_path = server_path.replace('\\', '/')
        if task_type == "upload":
            if file_type == "normal":
                path_dict["source-path"] = local_path
                path_dict["target-path"] = "/input/%s-%s/%s" % (
                    storage_id, user_id or self.user_id, server_path)
            elif file_type == "json":
                if not task_id:
                    raise TaskidNotexsit("The task ID must not be empty!")
                path_dict["source-path"] = local_path
                path_dict["target-path"] = "/input/%s-%s/%s/cfg" % (
                    storage_id, user_id or self.user_id, task_id)
            else:
                raise NotSupportfiletype(" %s is not supported file-type, "
                                         "currently only support normal and json!" % (file_type))
        elif task_type == "upload-list":
            path_dict["file-list"] = self.convert_upload(
                local_path, storage_id)
        elif task_type == "download":
            path_dict["source-path"] = "/%s/%s-%s/%s" % (
                downstorage, storage_id, user_id or self.user_id, server_path)
            path_dict["target-path"] = local_path
        else:
            raise NotSupportTasktype(" %s is not supported task-type, "
                                     "currently only support upload and download and upload-list!" % (task_type))
        return path_dict

    def start_transfer(self, server_ip, server_port, local_path, server_path, storage_id, input_id=None, task_type=None,
                       task_id=None, user_id=None, file_type="normal", downstorage="output", max_speed=None,
                       max_timeout=18000, network_mode=0, proxy_ip=None, proxy_port=None, enable_hash=False):
        """
        @:param server_ip: The IP address of the transport server
        @:param server_port: The IP address of the transport port
        @:param local_path: Local file path
        @:param server_path: server file path
        @:param storage_id: Various storage type ids eg:[input_id, output_id, config_id]
        @:param input_id: Various input storage type id
        @:param task_type: Transfer task Type eg:[download, upload, upload-list]
        @:param file_type: only to upload, eg:[normal, json]
        @:param max_speed: default is 1GB/S
        @:param max_timeout: Maximum time for querying task status
        @:param network_mode: Transport Protocol Type eg:[0, 1, 2]
        @:param proxy_ip: Proxy ip eg:10.14.88.66
        @:param proxy_port: Proxy port eg:5555
        @:param enable_hash: Enable hash verification.
        :return: statu code
        """
        # start service
        self.auto_download()
        self.listening_raysync_server()
        self.set_transfer_speed(max_speed, network_mode)
        self.set_proxy_manager(proxy_ip, proxy_port)
        if task_id not in self._task_failed_dict:  # first create task
            path_dict = self.get_transfer_path(
                task_type, local_path, server_path, storage_id, task_id, file_type, downstorage, user_id)
            mode_dict = {0: "default", 1: "tcp-only", 2: "udp-only"}
            storage_id = input_id if file_type == "json" else storage_id
            params = {
                "task-name": task_type,
                "server-ip": server_ip,
                "server-port": int(storage_id),
                "server-ssl-port": int(storage_id)-100,
                "renderbus-proxy-port": 32002,
                "proxy-port": 32002,
                "protocol-type": mode_dict[network_mode],
                "delay-threshold": 0,
                "account": self.user_name,
                "password": self.password,
                "group-id": 0,
                "enable-ssl": False,
                "enable-verify-hash": enable_hash,
            }
            params.update(path_dict)
            response = self.post(self._url.create_task, params)
            tranfer_task_id = response.get('task-id')
            self.logger.info(
                'Transfer task has been created. The Transfer task ID is %s' % (tranfer_task_id))
        else:  # 重新启动任务
            params = {
                "task-id": self._task_failed_dict[task_id],
            }
            response = self.post(self._url.start_task, params)
            tranfer_task_id = self._task_failed_dict[task_id]
            self.logger.info('Render task_id is %s,Transfer task id %s already try again......' % (
                task_id, tranfer_task_id))
        res_code = self.look_task_stauts(tranfer_task_id, task_id, max_timeout)
        return res_code

    def look_task_stauts(self, tranfer_task_id, task_id, max_timeout):
        """ look listening task status
            STATU_SLEEP: request task_status interface sleep(5s)
        """
        now_seconds = 0
        while True:
            if now_seconds >= max_timeout / STATU_SLEEP:
                raise TransferTimeout(
                    "Transmission timeout! The maximum transmission time is 5 hours by default!")
            now_seconds += 1
            time.sleep(STATU_SLEEP)
            params = {"task-id": tranfer_task_id}
            response = self.post(self._url.get_task_status, params)
            status = response["task-list"][0]["task-state"]
            if status in ["ready", "start", "idle"]:
                continue
            else:
                if status == "failed":
                    self._task_failed_dict[task_id] = tranfer_task_id
                elif status == "successful":
                    self._task_failed_dict.pop(task_id, None)
                else:
                    raise CreatTaskFailed(
                        "create transfer task failed! message is %s" % status)
                break
        result_code = self._resultDict.get(status)
        self.logger.info('The transmission task is complete and the status of the task is %s, result_code is %s!' % (
            status, result_code))
        return result_code

    def get_task_status(self, tranfer_task_id):
        """
            Querying Task Status
            :return:
        """
        self.listening_raysync_server()
        params = {"task-id": str(tranfer_task_id)}
        response = self.post(self._url.get_task_status, params)
        return response

    def get_task_list_status(self):
        """
            Querying Task List Status
        :return:
        """
        self.listening_raysync_server()
        params = {"task-group": "all"}
        response = self.post(self._url.get_task_list_status, params)
        return response
