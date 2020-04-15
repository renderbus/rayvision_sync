"""Transfer the required public functions."""

# Import built-in modules
from __future__ import print_function

from builtins import str
import logging
import subprocess
import sys
import time
import configparser

# Import third-party modules
from rayvision_sync.exception import RayvisionError

# Import local models
from rayvision_sync.constants import TASK_STATUS_DESCRIPTION


def print_to_log(cmd, logger):
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
    while True:
        result_line = cmd.stdout.readline()
        if result_line:
            result_line = result_line.strip()
            if result_line:
                if logger:
                    result_line = str2unicode(result_line)
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


def run_cmd(cmd_str, my_shell=True, print_log=True, flag=None, logger=None):
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

    err_messages = print_to_log(cmd_result, logger)
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
                                                 "be uploaded, please check")
                if result == 10:
                    time.sleep(time_interval)
                    time_interval += 10
                    if time_interval > 600:
                        time_interval = 600
                    logger.info("Retrying upload......")
                elif result == 9:
                    raise Exception("Parameter or domain name resolution"
                                    "error.")
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
