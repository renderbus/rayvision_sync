"""The Raysync util functions."""

# Import built-in models
from __future__ import unicode_literals

import os
import pathlib
import sys
from .exception import RayvisionError

# Python version.
VERSION = sys.version_info[0]


def convert_path(path):
    """Convert to the path the server will accept.

    Args:
        path (str): Local file path.
            e.g.:
                "D:/work/render/19183793/max/d/Work/c05/112132P-embery.jpg"

    Returns:
        str: Path to the server.
            e.g.:
                "/D/work/render/19183793/max/d/Work/c05/112132P-embery.jpg"

    """
    lower_path = path.replace('\\', '/')
    if lower_path[1] == ":":
        path_lower = lower_path.replace(":", "")
        path_server = "/" + path_lower
    else:
        path_server = lower_path[1:]

    return path_server


def upload_list_convert_list(upload_list_path):
    """
    Convert the asset list in TXT or JSON format to JSON format
    eg: upload_list.txt: D:/houdini/CG file/F
                         D:/houdini/CG file/F/houdini.hip
         toList: ["/D/houdini/CG file/F","/D/houdini/CG file/F/houdini.hip"]
    :return: file_list, tmp_upload.json
    """
    if not os.path.exists(upload_list_path):
        raise RayvisionError(
            1000006, "{} is not exist".format(upload_list_path))
    else:
        file_list = []
        with open(upload_list_path, "r") as f:
            for line in f.readlines():
                tmp = line.strip()
                tmp = convert_path(tmp)
                file_list.append(tmp)
        tmp_upload_path = os.path.join(
            os.path.dirname(upload_list_path), "tmp_upload.json")
        if os.path.exists(tmp_upload_path):
            os.remove(tmp_upload_path)
        pathlib.Path(tmp_upload_path).touch()
        return file_list, tmp_upload_path
