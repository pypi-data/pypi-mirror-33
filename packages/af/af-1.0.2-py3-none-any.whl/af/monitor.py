from multiprocessing import Process, Event
import time
from tqdm import tqdm

class Monitor(Process):

    def __init__(self, progress, total, report_frequency = 0.5):
        Process.__init__(self, )
        self._exit = False
        self._progress = progress
        self._total = total
        self._report_frequency = report_frequency
        self.exit = Event()

    def run(self):
        self._total_total = 0
        for i in self._total:
            self._total_total += i
        self._pbar = tqdm(total=self._total_total)
        self._last_progress = 0
        while not self.exit.is_set():
            self._update_bar()
            time.sleep(self._report_frequency)

        #pbar.update(progress - last_progress)
        #self._update_bar()
        return

    def _update_bar(self):
        self._total_progress = 0
        for i in self._progress:
            self._total_progress += i
        if self._total_progress <= self._total_total:
            self._pbar.update(self._total_progress - self._last_progress)
        else:
            self._pbar.close()
        self._last_progress = self._total_progress

    def shutdown(self):
        self.exit.set()

