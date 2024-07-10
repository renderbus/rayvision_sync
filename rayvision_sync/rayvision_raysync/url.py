from enum import Enum, unique


@unique
class ApiUrl(str, Enum):
    ''' Raysync interface list '''
    create_task = '/create-task'
    get_task_status = '/get-task-status'
    get_task_list_status = '/get-task-list'
    start_task = '/start-task'
    check_raysync_http = '/check-raysync-http'
    set_transfer_speed = '/set-transmission-parameters'
    set_proxy_manager = '/set-proxy-manager'
    get_file_list = '/get-file-list'
    set_task_limit = '/set-task-limit'
    get_task_limit = '/get-task-limit'

    def __format__(self, format_spec):
        return str.__format__(str(self._value_), format_spec)
