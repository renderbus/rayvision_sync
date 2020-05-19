import abc


class AbstractEngine(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def engine_type(self):
        """str: The type of the transmission."""
        pass

    @abc.abstractproperty
    def executable(self):
        pass

    @abc.abstractproperty
    def options(self):
        pass

    @abc.abstractproperty
    def get_command(self):
        pass

    @property
    def command(self):
        return self.get_command()

    @abc.abstractproperty
    def run_command(self):
        pass
