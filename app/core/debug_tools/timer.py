# timer.py
import time


class Timer:
    def __init__(self, countdown):
        self._start_time = None
        self.countdown = countdown

    def start(self):
        if self._start_time is None:
            self._start_time = time.process_time()
            print(f"Countdown: {self.countdown} seconds")

    def current(self):
        return int((time.process_time() - self._start_time))

    def is_running(self):
        if self._start_time is not None:
            return True
        return False

    def stop(self):
        if self._start_time is not None:
            elapsed_time = time.process_time() - self._start_time
            self._start_time = None
            print(f"Elapsed time: {elapsed_time:0.5f} seconds")

    def is_expired(self):
        if self._start_time is not None:
            if (time.process_time() - self._start_time) >= self.countdown:
                return True
            return False

    def restart(self):
        if self._start_time is not None:
            print("Restarting!")
            self._start_time = time.process_time()

    def renew(self, extra_time):
        if self._start_time is not None:
            print("Adding extra time: ", extra_time)
            self._start_time += extra_time


if __name__ == "__main__":

    counter = MyCounter(countdown=2)
    counter.start()
    while True:
        if counter.is_expired():
            counter.stop()
            break
