from ctypes import *
import platform
import os
import threading
import jsonpickle

zhe_rid_t = c_uint8
zhe_pubidx_inner_t = c_uint8
zhe_subidx_inner_t = c_uint8
zhe_paysize_t = c_uint16
zhe_time_t = c_uint32

class zhe_pubidx_t(Structure):
    _fields_ = [('idx', zhe_pubidx_inner_t)]

class zhe_subidx_t(Structure):
    _fields_ = [('idx', zhe_subidx_inner_t)]

SUB_HANDLER_PROTO = CFUNCTYPE(None, zhe_rid_t, c_char_p, zhe_paysize_t, c_void_p)


def get_lib_ext():
    system = platform.system()
    if system == 'Linux':
        return '.so'
    elif system == 'Darwin':
        return '.dylib'
    else:
        return '.dll'

def get_user_lib_path():
    system = platform.system()
    if system == 'Linux':
        return '/usr/local/lib'
    elif system == 'Darwin':
        return '/usr/local/lib'
    else:
        return '/usr/local/lib'


zhelib = get_user_lib_path() + os.sep + 'libdzhe' + get_lib_ext()

zhe = None

ZHE_DEFAULT_PORT = 7447

class Zhe(object):
    def __init__(self):
        self.zhelib = CDLL(zhelib)

        ## zhe_time_t zhe_platform_time(void)
        self.zhelib.zhe_platform_time.restype = zhe_time_t
        self.zhelib.zhe_platform_time.argtypes = None

        self.zhelib.zhe.restype = c_void_p
        self.zhelib.zhe.argtypes = [c_uint16]

        self.zhelib.zhe_declare_resource.restype = c_bool
        self.zhelib.zhe_declare_resource.argtypes = [zhe_rid_t, c_char_p]

        self.zhelib.zhe_publish.restype = zhe_pubidx_t
        self.zhelib.zhe_publish.argtypes = [zhe_rid_t, zhe_paysize_t, c_int]

        self.zhelib.zhe_subscribe.restype = zhe_subidx_t
        self.zhelib.zhe_subscribe.argtypes = [zhe_rid_t, zhe_paysize_t, c_uint, SUB_HANDLER_PROTO ,c_void_p]

        # int zhe_write(zhe_pubidx_t pubidx, const void *data, zhe_paysize_t sz, zhe_time_t tnow);
        self.zhelib.zhe_write.restype = c_int
        self.zhelib.zhe_write.argtypes = [zhe_pubidx_t, c_void_p, zhe_paysize_t, zhe_time_t]

        # int zhe_write_uri(const char *uri, const void *data, zhe_paysize_t sz, zhe_time_t tnow);
        self.zhelib.zhe_write_uri.restype = c_int
        self.zhelib.zhe_write_uri.argtypes = [c_char_p, c_void_p, zhe_paysize_t, zhe_time_t]

        # void zapi_dispatch(uint platform)
        self.zhelib.zhe_dispatch.restype = None
        self.zhelib.zhe_dispatch.argtypes = [c_void_p]

        self.zhelib.zhe_once.restype = None
        self.zhelib.zhe_once.argtypes = [c_void_p, c_uint64]

        self.zhelib.zhe_loop.restype = None
        self.zhelib.zhe_loop.argtypes = [c_void_p, c_uint64]


        self.zhelib.zhe_flush.restype = None
        self.zhelib.zhe_flush.argtypes = None

        self.platform = self.zhelib.zhe(ZHE_DEFAULT_PORT, 0)
        self.running = False

    @staticmethod
    def __run():
        z = Zhe.instance()
        if z.running == False:
            z.running = True
            print('>>> Starting Runtime')
            while z.running:
                z.run_once(100000000)



    def stop(self):
        self.running = False


    def start(self):
        self.runner = threading.Thread(target=self.__run, args=())
        self.runner.daemon = True
        self.runner.start()


    def run_once(self, p):
        self.zhelib.zhe_once(self.platform, p)

    def dispatch(self):
        self.zhelib.zhe_dispatch(self.platform)

    def publish(self, rid, cid, reliable):
        id = self.zhelib.zhe_publish(rid, cid, reliable)
        # pid = zhe_pubidx_t()
        # pid.idx = id
        return id

    def subscribe(self, rid, fun):
        return self.zhelib.zhe_subscribe(rid, 0, 0, fun, None)

    def write(self, pubid, data):
        l = len(data)
        return self.zhelib.zhe_write(pubid, data, l,  self.now())

    def write_obj(self, pubid, o):
        payload = jsonpickle.encode(o).encode()
        l = len(payload)
        return self.zhelib.zhe_write(pubid, payload, l, self.now())

    def write_obj_uri(self, pubid, uri, o):
        payload = jsonpickle.encode(o).encode()
        l = len(payload)
        return self.zhelib.zhe_write_uri(uri, payload, l, self.now())

    # c_char_p, c_void_p, zhe_paysize_t, zhe_time_t
    def write_uri(self, uri, data):
        l = len(data)
        return self.zhelib.zhe_write_uri(uri, data, l, self.now())

    def flush(self):
        self.zhelib.zhe_flush()

    def now(self):
        return self.zhelib.zhe_platform_time()

    def run_loop(self, period):
        self.zhelib.run_loop(period)

    def payload2string(self, payload, len):
        return str(payload[:len], 'utf-8')

    def payload2object(self, payload, len):
        return jsonpickle.decode(self.payload2string(payload,len))

    @staticmethod
    def instance():
        global zhe
        if zhe is None:
            zhe = Zhe()

        return zhe



