from abc import ABC, abstractmethod
import logging
default_logger = logging.getLogger(__name__)

class CocoBaseProducer(ABC):
    def __init__(self, conf, logger = None):
        self._config = conf
        self._logger = logger if logger else default_logger

        super().__init__()


    @abstractmethod
    def connect(self):
        pass


    @abstractmethod
    def send(self, data):
        pass


    @abstractmethod
    def close(self):
        pass

