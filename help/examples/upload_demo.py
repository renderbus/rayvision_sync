"""Upload demo."""

from rayvision_sync.transfer import RayvisionTransfer
from rayvision_sync.upload import RayvisionUpload


USER_INFO = {
    'config_bid': '30201',
    'input_bid': '10202',
    'user_id': '100093088',
    'domain': 'tasks.renderbus.com',
    'platform': '2',
    "local_os": 'windows'
}
CONFIG_PATH = [
    r"C:\workspace\work\9447896\tips.json",
    r"C:\workspace\work\9447896\task.json",
    r"C:\workspace\work\9447896\asset.json",
    r"C:\workspace\work\9447896\upload.json",
]


TRANS = RayvisionTransfer(**USER_INFO)
UPLOAD = RayvisionUpload(TRANS)
UPLOAD.upload_config("9449022", CONFIG_PATH)
