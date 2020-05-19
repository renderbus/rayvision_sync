from rayvision_sync.api import TransmissionEngine


class RaySync(TransmissionEngine):

    @property
    def engine_type(self):
        return "sync"

    def upload(self):
        self.options = [
            'upload'
        ]
        self.deliver()

    def download(self, args):
        self.options = [args]
        self.deliver()
