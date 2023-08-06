from abc import ABC, abstractmethod
import logging
default_logger = logging.getLogger(__name__)

class CocoBaseWorker(ABC):
    def __init__(self, conf, seq, logger = None):
        self._config = conf
        self._seq = seq
        self._logger = logger if logger else default_logger
        super().__init__()


    @abstractmethod
    def process(self, data):
        pass
