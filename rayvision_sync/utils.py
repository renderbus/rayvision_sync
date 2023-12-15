"""Transfer the required public functions."""

# Import built-in modules
from __future__ import print_function

import codecs
import json
import logging
import os
import re
import subprocess
import sys
import time

import configparser
from builtins import str

# Import local models
from rayvision_sync.constants import TASK_STATUS_DESCRIPTION
# Import third-party modules
from rayvision_sync.exception import RayvisionError


def print_to_log(cmd, logger, is_record=False, redis_flag=None, redis_obj=None):
    """Output the CMD command information.

    If there is an error in the log, it will be recorded in a list.

    Args:
        cmd (subprocess.Popen): The object obtained by executing the cmd
            command.
        logger (func): The log function.
            .e.g:
                SDK_LOG.info.

    Returns:
        list: All errors output by the cmd command.

    """
    err_messages = []
    if is_record and not redis_obj:
        import redis
        redis_obj = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
    while True:
        result_line = cmd.stdout.readline()
        if result_line:
            result_line = result_line.strip()
            if result_line:
                result_line = str2unicode(result_line)
                if is_record:
                    complite = re.compile(".*?upload file done.*?\((.*?)\).*")
                    obj = re.search(complite, result_line)
                    if obj:
                        upload_done_file = obj.group(1).strip()
                        insert_redis(path=upload_done_file, redis_db=redis_obj, redis_flag=redis_flag)

                if logger:
                    logger(result_line)
                    if ('upload file fail' in result_line or
                            ('get path' in result_line and
                             'info failed' in result_line)):
                        err_messages.append(result_line)
        else:
            break
    return err_messages


def handle_cmd_result(flag, returncode, err_messages, logger=None):
    """Process cmd results.

    Perform the corresponding operation according to the status code.
    0 means success, 11 means unable to retry, 10 means retry,9 means
    parameter or domain name resolution error.

    Args:
        flag (bool): Used to identify uploads.
        returncode (int): The status code returned by cmd after execution.
        err_messages (list of str): List of error messages.
        logger (logging.info or logging.debug): Log output object method.

    Returns:
        int: Status code.

    """
    logger = logger or logging.getLogger(__name__)
    if flag and returncode == 0:
        pass
    elif flag and returncode == 11:
        for err_message in err_messages:
            logger("err_message: %s", err_message)
        logger("cmdp.returncode: %s", returncode)
        logger("Upload failed, there has non-uploadable files")

    elif flag and returncode == 10:
        for err_message in err_messages:
            logger("err_message: %s", err_message)
        logger("cmdp.returncode: %s", returncode)
        logger("Err_message has files that have not been uploaded"
               " successfully, will enter retry upload ")

    elif flag and returncode == 9:
        for err_message in err_messages:
            logger("err_message: %s", err_message)
        logger("cmdp.returncode: %s", returncode)
        logger("Parameter or domain name resolution error.")

    return returncode


def run_cmd(cmd_str, my_shell=True, print_log=True, flag=None, logger=None, is_record=False, redis_flag=None,
            redis_obj=None):
    """Run cmd.

    If the cmd runs with an error, it will print the error message and return
    to False.

    Args:
        cmd_str (str): String of the cmd command.
        my_shell (bool, optional): Accept a string type variable as a command
            and call the shell to execute the string.
        print_log (bool, optional): Print log, True: print, False: not print.
        flag (bool, optional): default is None.
        logger (logging, optional): Log object.
        redis_obj (object, optional): redis object

    Returns:
        bool: True is success, False is wrong.

    """
    if not logger:
        logger = logging.getLogger(__name__)

    if print_log:
        logger = logger.info
    else:
        logger = logger.debug

    logger(u'cmd...%s', str2unicode(cmd_str))

    if sys.version_info[0] == 2:
        cmd_str = str2unicode(cmd_str)
        cmd_str = cmd_str.encode(sys.getfilesystemencoding())


    cmd_result = subprocess.Popen(cmd_str, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  shell=my_shell)

    err_messages = print_to_log(cmd_result, logger, is_record=is_record, redis_flag=redis_flag, redis_obj=redis_obj)
    cmd_result.communicate()
    returncode = cmd_result.returncode
    return handle_cmd_result(flag, returncode, err_messages, logger)


def upload_retry(func):
    """Determine whether to retry according to the status code of cmd."""

    def inner(*args, **kwargs):
        """Handle."""
        time_interval = 5
        times = 0
        logger = logging.getLogger(__name__)
        while True:
            result = func(*args, **kwargs)
            if result == 0:
                return True
            if times > 10:
                if result == 11:
                    raise RayvisionError(200025, "There are files that cannot"
                                                 "be uploaded, please check the file is exists.")
                if result == 10:
                    time.sleep(time_interval)
                    time_interval += 10
                    if time_interval > 600:
                        time_interval = 600
                    logger.info("Retrying upload......")
                elif result == 9:
                    raise Exception("Parameter or domain name resolution"
                                    "error.")
                elif result in [1, 2, 3, 4, 5, 6, 7, 8]:
                    raise RayvisionError(200024, "argument format invalid"
                                                 "please check the argument.")
            else:
                times += 1
                logger.info("Retrying upload......")

    return inner


def str2unicode(handle_str, str_decode='default'):
    """Decode the string.

    Args:
        handle_str (str): String to be decoded.
        str_decode (str, optional): What encoding needs to be decoded,
            the default is lowercase.

    Returns:
        str: Need to decode the string.

    """
    if not isinstance(handle_str, str):
        try:
            if str_decode != 'default':
                handle_str = handle_str.decode(str_decode.lower())
            else:
                try:
                    handle_str = handle_str.decode('utf-8')
                except (AttributeError, UnicodeError):
                    try:
                        handle_str = handle_str.decode('gbk')
                    except (AttributeError, UnicodeError):
                        handle_str = handle_str.decode(
                            sys.getfilesystemencoding())
        except (AttributeError, UnicodeError) as err:
            logger = logging.getLogger(__name__)
            logger.warning('str2unicode:decode failed')
            logger.warning(str(err))
    return handle_str


def get_task_status_description(task_status_code=None, language='1'):
    """Get task status description.

    Get the status of the task now by the task status code.

    Args:
        task_status_code (str): Task status code.
        language (str): Language, "0": Simplified Chinese; "1": English

    Returns:
        str: Task status information.
            e.g.:
                "Waiting".

    Raises:
        RayvisionError: Task status code is None.

    """
    try:
        task_status_description = TASK_STATUS_DESCRIPTION.get(
            task_status_code, {})[language]
        return task_status_description
    except KeyError:
        logger = logging.getLogger(__name__)
        logger.error('Get empty task_status_description,'
                     ' Please check the input.')
        raise RayvisionError(1000000, "Get empty task_status_description,"
                                      " Please check the input")

def get_share_info(api):
    """Get the main account information.

    Args:
        api: api object.

    Returns:

    """
    user_profile = api.user.query_user_profile()
    share_main_capital = user_profile.get("shareMainCapital", 0)
    if share_main_capital == 0:
        main_input_bid = api.user_info['input_bid']
        main_user_id = api.user_info['user_id']
    else:
        user_transfer_bid = api.user.get_transfer_bid()
        main_input_bid = user_transfer_bid.get("parent_input_bid")
        main_user_id = user_profile.get("mainUserId")
    return main_input_bid, main_user_id


def create_transfer_params(api):
    """Takes a parameter from the authentication object.

    Args:
        api: Objects that have been authenticated.

    Returns:
        dict

    """
    params = {
        'config_bid': api.user_info['config_bid'],
        'input_bid': api.user_info['input_bid'],
        "output_bid": api.user_info["output_bid"],
        "domain": api.user_info['domain'],
        "platform": api.user_info['platform'],
        "local_os": api.user_info['local_os'],
        "user_id": api.user_info['user_id'],
    }
    return params


def read_ini_config(db_config_path):
    """read ini file"""
    conf = configparser.ConfigParser()
    conf.read(db_config_path, encoding="utf-8")
    return conf


def json_load(json_path, encoding='utf-8'):
    """Load the data from the json file.

    Args:
        json_path (str): Json file path.
        encoding (str): Encoding, default is ``utf-8``.

    Returns:
        dict: Data in the json file.
            e.g.:
                {
                    "task_info"
                }

    """
    if os.path.exists(json_path):
        with codecs.open(json_path, 'r', encoding=encoding) as f_json:
            data = json.load(f_json)

        return data


def write_json(path, info):
    """write json file."""
    with codecs.open(path, 'w', 'utf-8') as f_tips_json:
        json.dump(info, f_tips_json, indent=4, ensure_ascii=False)


def cutting_upload(upload_path, max_resources_number=None, after_cutting_position=None):
    """Cut upload.json according to the number of custom files.

    Args:
        upload_path (str): upload.json absolute path.
        max_resources_number (int): Maximum number of resources in each upload file.
        after_cutting_position (str): save location of upload file generated after cutting.

    Returns:
        list: Absolute path of all upload files generated after cutting, excluding original upload files.
            e.g.:
                ['D:\\test\\test_upload\\1586250829\\upload_1.json',
                'D:\\test\\test_upload\\1586250829\\upload_2.json']

    """
    if not os.path.exists(upload_path):
        raise RayvisionError(200001, "upload file is not exist: {}".format(upload_path))
    if max_resources_number is None:
        return [upload_path]
    if after_cutting_position is None or not os.path.exists(after_cutting_position):
        after_cutting_position = os.path.dirname(upload_path)

    upload_info = json_load(upload_path)
    asset = upload_info.get("asset", [])
    if max_resources_number >= len(asset):
        return [upload_path]
    count = 1
    cut_json_pool = []
    for per_index in range(0, len(asset) + 1, max_resources_number):
        if per_index == 0:
            cut_per_info = asset[0:max_resources_number]
        else:
            cut_per_info = asset[per_index:per_index + max_resources_number]
        cut_info = {"asset": cut_per_info}
        to_path = os.path.normpath(os.path.join(after_cutting_position, "upload_{}.json".format(str(count))))
        write_json(to_path, cut_info)
        count += 1
        cut_json_pool.append(to_path)
    return cut_json_pool


def insert_redis(path, redis_db, redis_flag=None):
    """Record upload file information to Redis.

    Args:
        path (str): file path.
        redis_db (redis object): redis handle.
        redis_flag (): Redis database tag.

    Returns:

    """
    redis_flag = redis_flag if redis_flag else "upload_done"
    redis_db.hset(redis_flag, path, int(time.time()))

