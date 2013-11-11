import time

class Timer():
    def __init__(self, name=None, report=True):
        self.report = report
        if name is None:
            self.name = 'task'
        else:
            self.name = name
    def __enter__(self):
        self.start = time.time()
    def __exit__(self, *args):
        if self.report is True:
            message = '[wil] [timer]: time elapsed for {0} was: {1}'
            print(message.format(self.name, str(time.time() - self.start)) )
