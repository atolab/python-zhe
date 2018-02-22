from zhe import *
import os
import time
import jsonpickle
import random

class TempSensor(object):
    def __init__(self, id, t, h):
        self.id = id
        self.temp = t
        self.hum = h

if __name__ == '__main__':
    z = Zhe.instance()
    z.start()
    pub = z.publish(1, 0, 1)
    ts = TempSensor(1, random.uniform(0, 50), random.uniform(30, 100))
    while True:
        data = jsonpickle.encode(ts)
        z.write(pub, data.encode())
        z.flush()
        ts.temp = random.uniform(0, 50)
        ts.hum = random.uniform(30, 100)
        time.sleep(1)