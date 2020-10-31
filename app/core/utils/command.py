class Command:
    
    def __init__(self):
        self._cmd = "IDLE"

    def __call__(self):
        return self._cmd

    def set(self, cmd):
        if self._cmd != cmd:
            self._cmd = cmd

    def reset(self):
        self._cmd = "IDLE"