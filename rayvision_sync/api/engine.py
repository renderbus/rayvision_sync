import os
from rayvision_sync.api.abstract_engine import AbstractEngine


class TransmissionEngine(AbstractEngine):
    settings = {}

    def __init__(self, executable=None):
        self._command = None
        self._executable = executable

    @property
    def _app_env_name(self):
        return "RAYVISION_{}".format(self.engine_type.upper())

    @property
    def executable(self):
        app = os.getenv(self._app_env_name)
        if not self._executable and app:
            self._executable = app
        return self._executable

    def get_command(self):
        if not self.executable:
            raise TypeError(
                'Required "executable" not specified. Pass as argument or set '
                'in environment variable {}.'.format(self._app_env_name)
            )
        return [self.executable, self.options]

    @property
    def options(self):
        return self._command

    @options.setter
    def options(self, command_options):
        if isinstance(command_options, list):
            command_options = " ".join(command_options)
        self._command = command_options

    def run_command(self):
        return self.command

    def process(self):
        pass

    def finish(self):
        pass

    def deliver(self):
        self.run_command()
        self.finish()
