from zhe import *
import jsonpickle

class TempSensor(object):
    def __init__(self, id, t, h):
        self.id = id
        self.temp = t
        self.hum = h

@SUB_HANDLER_PROTO
def handler(rid, data, size, attch):
    s = str(data[:size], 'utf-8')
    ts = jsonpickle.decode(s)
    print('>> rid: {} ->  TempSensor({}, {}, {})'.format(rid, ts.id, ts.temp, ts.hum))


if __name__ == '__main__':
    z = Zhe.instance()
    z.subscribe(1, handler)
    while True:
        z.dispatch()