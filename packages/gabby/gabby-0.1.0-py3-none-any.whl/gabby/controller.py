import logging
from multiprocessing import Process

from .gabby import Gabby


class Controller:
    _instance = None

    def __new__(cls, thread=False):
        """
        Singleton implementation
        """
        if Controller._instance is None:
            obj = object.__new__(cls)
            Controller._instance = obj
            Controller._instance.gabbies = []
        return Controller._instance

    def add_gabby(self, gabby):
        if isinstance(gabby, Gabby):
            self.gabbies.append(gabby)
        else:
            raise TypeError('You can only add Gabby objects')

    def run(self):
        """
        Run a process for each 2RSystem sub module
        """
        runner_procs = [self._run_instance(x) for x in self.gabbies]

        for proc in runner_procs:
            proc.join()

        logging.info("[Success] Shutted down")

    def _run_instance(self, gabby):
        """
        Start a new process to execute a given function
        """
        logging.info(f'Starting module')
        proc = Process(target=gabby.run)
        proc.start()
        return proc
