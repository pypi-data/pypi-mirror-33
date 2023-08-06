from abc import ABC, abstractmethod
import logging
default_logger = logging.getLogger(__name__)

class CocoBaseConsumer(ABC):
    def __init__(self, conf, worker, logger = None):
        self._config = conf
        self._worker = worker
        self._logger = logger if logger else default_logger
        super().__init__()


    @abstractmethod
    def connect(self):
        pass
