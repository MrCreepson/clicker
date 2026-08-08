import sys

class StdoutProxy:
    def __init__(self):
        self.buffer = ""
        self._stdout = sys.__stdout__

    def write(self, text):
        self.buffer += text
        self._stdout.write(text)  # nadal terminal

    def flush(self):
        self._stdout.flush()

    def getvalue(self):
        return self.buffer