#encoding=utf8
import os,time,glob,thread,threading
from datetime import datetime

upcount = 0
class Operation(threading._Timer):
    def __init__(self, *args, **kwargs):
        threading._Timer.__init__(self, *args, **kwargs)
        self.setDaemon(True)

    def run(self):
        while True:
            self.finished.clear()
            self.finished.wait(self.interval)
            if not self.finished.isSet():
                self.function(*self.args, **self.kwargs)
            else:
                return self.finished.set()

class Manager(object):

    ops = []

    def add_operation(self, operation, interval, args=[], kwargs={}):
        op = Operation(interval, operation, args, kwargs)
        self.ops.append(op)
        thread.start_new_thread(op.run, ())

def scanDB():
    global upcount                                 
    NOW = datetime.now()
    if NOW.hour == 11 :
           if upcount == 0:
               print str(NOW) + 'start...'
               os.system('python mycmmd.py')
               upcount = 1

    else:
        upcount = 0
    pass


if __name__ == "__main__":
    

    print 'run','...'*10
    timer = Manager()
    timer.add_operation(scanDB,1)
    while 1:
	pass


