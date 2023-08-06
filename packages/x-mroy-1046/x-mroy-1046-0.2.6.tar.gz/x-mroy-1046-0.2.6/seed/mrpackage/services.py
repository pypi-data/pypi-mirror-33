from socketserver import BaseRequestHandler, UDPServer
from socket import socket, AF_INET, SOCK_DGRAM
from socket import timeout
import time
import base64
import json
import sys
import os
import pickle
from socketserver import BaseRequestHandler, UDPServer

import rsa
from seed.mrpackage.libs import pubip_rsa
from seed.mrpackage.libs import Rsa
from seed.mrpackage.libs import Format, deFormat
from seed.mrpackage.libs import loger
import seed.mrpackage.oscmd as oscmd
from seed.mrpackage.oscmd import Os
from seed.mrpackage.oscmd import FileHandle
from seed.mrpackage.daemon import Daemon
from seed.mrpackage.config import MODULE_PATH
from seed.mrpackage.config import DB_PATH,Host,Cache

import seed.mrpackage.api as APIS
from asynctools.servers import Connection
import importlib


from qlib.data import Cache, dbobj
sys.path += [MODULE_PATH]

log = loger()
UDP_PORT = 60077
UDP_PORT_BAK = 60078

class Reg(dbobj):pass

class ModuleMixin:

    def ls(self):
        return os.listdir(MODULE_PATH)

    def use(self, name):
        self.module = importlib.import_module(name)

    def attrs(self):
        return self.module.__dir__()

    def call(self, name, *args, **kwargs):
        if hasattr(self.module, name):
            try:
                res = getattr(self.module, name)(*args, **kwargs)
            except Exception as e:
                res = e

        else:
            res = Exception("no {} in {}".format(name, self.module.__name__))
        return pickle.dumps(res)

class DaemonServer(BaseRequestHandler):
    def handle(self):
        msg, self.sock = self.request
        if msg == b'hello':
            self.sock.sendto(b"i am ok", self.client_address)
            return
        resp = time.ctime()
        log.info(resp + " | Handle | %d len recv" % len(msg)  + str(self.client_address))
        if isinstance(msg, bytes):
            if msg == b'-v':
                self.sock.sendto(b"fuck", self.client_address)
            # return
        self.just_go(msg)

    def reply(self, id, op, msg, decoder=''):
        e = Format(msg, op=op, id=id, decoder=decoder)
        log.info("send {} bytes to client ".format(len(e)))
        if len(e) > 1024:
            al = len(e)
            l = al // 1024
            for i in range(l):
                log.info("send no.%d" % i)
                dd = e[i*1024:(i+1) * 1024] + b'[continu@]'
                log.error("block: (len:{}) {} {}".format(len(dd),i, dd))
                self.sock.sendto(dd, self.client_address)
            if l * 1024 < al:
                log.info("send finish")
                self.sock.sendto(e[l*1024:], self.client_address)
            else:
                log.info("send finish")
        else:
            self.sock.sendto(e, self.client_address)

    def just_go(self, msg):
        recived_msg = deFormat(msg)
        id = recived_msg['id']
        op = recived_msg['op']
        from_id = recived_msg['from_id']
        msg = recived_msg['msg']
        cmd = 'List'
        m = 'Os'
        if_decrypted = recived_msg['if_rsa']
        log.info(b"operating: " + op)
        if op == b"reg":
            self.reg(from_id, msg, if_decrypted)
        elif op == b'os':
            if msg.decode().count("::") > 0:
                cmd, arg = msg.decode("utf8").split("::", 1)
            elif msg.decode().count("::") > 1:
                m, cmd, arg = msg.decode('utf8').split("::",2)
            else:
                arg = None
                cmd = msg.decode('utf8')
            self.os_run(from_id, cmd, arg, module=m)

        elif op == b'base':
            self.base_init(from_id)
        elif op == b'rpc':
            self.script(from_id, msg)
            
        elif op == b'add_moudle':
            self.add_moudle(from_id, msg)

        elif op == b'circle':
            circle = oscmd.ProxyCircle()
            need_loads = False
            if msg.count(b"::") > 0:
                cmd, args = msg.split(b"::",1)
                cmd = cmd.decode()
                args = pickle.loads(base64.b64decode(args))
                r = print
                try:
                    r = getattr(circle, cmd)
                except AttributeError as e:
                    self.reply(from_id, {'result':e}, decoder='pickle')
                    return
                need_loads = False
                try:
                    res = r(*args['args'], **args['kargs'])
                except Exception as e:
                    res = base64.b64encode(pickle.dumps(e)).decode('utf8')
                    need_loads = True
                if not isinstance(res, (str, int, bool, list, dict,)):
                    try:
                        res = pickle.dumps(res)
                    except Exception as e:
                        res = pickle.dumps(e)
                    need_loads = True
            else:
                r = getattr(circle, msg.decode().strip())
                res = r()
                if not isinstance(res, (str,int, bool, list, dict,)):
                    try:
                        res = base64.b64encode(pickle.dumps(res)).decode('utf8')
                        need_loads = True
                    except Exception as e:
                        res = base64.b64encode(pickle.dumps(e)).decode('utf8')
                        need_loads = True

            s = {'result' : res, 'pickle': need_loads}
            self.reply(from_id, "reply", s, decoder='json')

        elif op ==b'script':
            self.scirpt(from_id, msg)


        elif op == b'reset':
            self.reset(from_id)

        elif op == b'check':
            o = Os()
            msgr = []
            for i in ['python3', 'pip3', 'tor', 'proxychains', 'sslocal']:
                service = {}
                service['name'] = i
                if o.check(i):
                    log.info("[o] -> " + i)
                    service['if_install'] = True
                    
                else:
                    log.info("[x] -> " + i)
                    service['if_install'] = False
                msgr.append(service)
            self.reply(from_id, "reply", {"data":msgr}, decoder='json')

        elif op == b'log':
            line = msg
            self.os_log(from_id, line)

        elif op == b'reinstall':
            if msg == 'main':
                os.popen("x-rexlay stop || pip3 uninstall -y x-mroy-1046 && pip3 install x-mroy-1046  --no-cache-dir && x-relay start ")
            elif msg == 'bak':
                os.popen("x-bak stop || pip3 uninstall -y x-mroy-1046 && pip3 install x-mroy-1046  --no-cache-dir && x-bak start ")
        elif hasattr(APIS, op.decode('utf8')):
            Handler_m = getattr(APIS, op.decode("utf8"))
            h = Handler_m(from_id, op.decode("utf8"), msg.decode("utf8"))
            self.reply(from_id,"reply", h.res)

        else:
            self.reply(from_id, "reply", "regist_to_server!!")

    def script(self, from_id, msg):
        m = ModuleMixin()
        res = m.run_from_json(msg)
        self.reply(from_id, 'reply', {'res':res}, decoder='pickle')

    def add_moudle(self, from_id, msg):
        n = msg['name']
        f = msg['file']
        with open(os.path.join(MODULE_PATH, n), 'wb') as fp:
            fp.write(f)
        res = os.listdir(MODULE_PATH)
        self.reply(from_id,'reply', {"res":res}, decoder='json')

    def base_init(self, id):
        circle = oscmd.ProxyCircle()
        pids = circle.GetStatus()
        self.reply(id, "reply", pids, decoder='json')

    def reset(self, id):
        o = Os()
        self.reply(id, "reply", "reset to clear", decoder='str')
        o.Uninstall("tor")
        o.Uninstall("proxychains")

    def reg(self,id, msg, if_decrypted):
        log.info("if pass load key : " + str(if_decrypted))
        pubip_rsa.import_key(msg)
        log.info("reply" + str(self.client_address))
        server_pub = pubip_rsa.export_key()
        self.reply(id, "pub_key", server_pub, decoder='base64')

    def os_run(self, id,command, args, module='Os'):
        if hasattr(oscmd, module):
            M = getattr(oscmd, module)
        else:
            M = Os
        os_controller = M()
        if hasattr(os_controller, command):
            c = getattr(os_controller, command)
            if args == None:
                res = {'result': c()}
            else:
                res = {'result': c(args)}
            self.reply(id, "reply", res, decoder='json')
        else:
            self.reply(id, "reply", "not found method" + command, decoder='str')

    def exchange_pub(self, ip):
        b = Bitter(ip)
        b.regist_to_server()

    def get_pub(self, id, pub):
        k = pubip_rsa.export_key()
        pubip_rsa.import_key(k)
        self.sock.sendto(k, self.client_address)

    def os_log(self, id, line):
        os_controller = Os()
        res = os_controller.stdout(line)
        log.info(res)
        if isinstance(res, bytes):
            res = res.decode("utf8")
        self.reply(id, "reply", res, decoder='log')

class ModuleMixin:

    def ls(self):
        return os.listdir(MODULE_PATH)

    def use(self, name):
        self.module = importlib.import_module(name)

    def attrs(self):
        return self.module.__dir__()

    def run_from_json(self, msg):
        if isinstance(msg, bytes):
            lib,fun, arg = msg.split(b'::',2)
            self.use(lib.decode())
            real_args = pickle.loads(arg)
            log.info("call : rpc")
            res = self.call(fun.decode(),*real_args['args'], **kargs['kwargs'])
            log.debug(res)
            return res
        elif isinstance(msg, dict):
            if msg['op'] == 'ls':
                res = os.listdir(MODULE_PATH)
                return res
            else:
                lib = msg['lib']
                fun = msg['fun']
                args = pickle.loads(msg['args'])
                kwargs = pickle.loads(msg['kwargs'])
                self.use(fun)
                res = self.call(fun, *args, **kwargs)
                return res


    def call(self, name, *args, **kwargs):
        if hasattr(self.module, name):
            try:
                log.debug("call : " + name)
                res = getattr(self.module, name)(*args, **kwargs)
            except Exception as e:
                res = e

        else:
            res = Exception("no {} in {}".format(name, self.module.__name__))
        return pickle.dumps(res)

class Bitter:
    def __init__(self, ip, port=UDP_PORT, async_rpc=False):
        self.ip = ip
        self.port = port
        self.op = 'circle'
        self._if_async_rpc = async_rpc
        self.callback = print

    @property
    def async(self):
        return self._if_async_rpc

    def log(self, id=id, line=5):
        recv = self.sendto(str(line), op='log')
        return recv

    def _callback(self, data):
        fr = data['from_id']
        if 'res' in data['msg']:
            res = pickle.loads(data['msg']['res'])
        else:
            res = data
            if 'msg' in res:
                res = res['msg']
            if 'result' in res:
                res = res['result']
            if 'data' in res:
                res = res['data']
                print(type(res))
        self.callback([fr, res])

    def setop(self, op):
        self.op = op

    def add_moudle(self, f):
        if os.path.exists(f):
            c = b''
            with open(f, 'rb') as fp:
                c = fp.read()
            name = os.path.basename(f)
            res = self.sendto({
                    'name':name,
                    'file':c,
                }, op='add_moudle', decoder='pickle')

    def help(self):
        res = self.sendto("List", op=self.op)
        return res

    def __getattr__(self, func_name):

        def _rpc(*args, **kwargs):
            if self.op == 'rpc':
                if '.' in func_name:
                    lib, fun = func_name.split(".",1)
                else:
                    lib = func_name
                    fun = func_name
                msg = {
                    'args': pickle.dumps(args),
                    'kwargs': pickle.dumps(kwargs),
                    'op':func_name,
                    'lib':lib,
                    'fun':fun
                }
                if self.async:
                    return self.async_send(msg, self._callback, op=self.op, decoder='pickle')
                r = self.sendto(msg, op=self.op, decoder='pickle')
                if not r:
                    return 'no recive msg'
                if 'msg' in r and 'pickle' in r['msg']:
                    if r['msg']['pickle']:
                        return pickle.loads(r['msg']['result'])
                return r['msg']
            else:
                log.info("Run :" + func_name +" ||" + self.ip)
                arg_bytes = base64.b64encode(pickle.dumps({'args':args,'kargs': kwargs}))
                r = None
                if self.async:
                    return self.async_send("::".join([func_name, arg_bytes.decode()]), self._callback, op=self.op)
                else:
                    r = self.sendto("::".join([func_name, arg_bytes.decode()]), op=self.op)
                if not r:
                    return 'no recive msg'
                if 'msg' in r and 'pickle' in r['msg']:
                    if r['msg']['pickle']:
                        return pickle.loads(r['msg']['result'])
                return r['msg']
        return _rpc

    def async_rpc(self, func, callback, *args, loop=None, policy=None,decoder='', **kwargs):
        arg_bytes = base64.b64encode(pickle.dumps({'args':args,'kargs': kwargs}))
        log.debug("rpc : "+func)
        self.async_send("::".join([func, arg_bytes.decode()]), callback, op=self.op,  decoder = decoder,policy=policy, loop=loop)


    def _sock_send(self, msg, wait=True, callback=None):
        # con = Connection(self.ip, self.port,'udp')
        # for i in range(3):
        #     try:
        #         con.write(msg)
        #         if wait:
        #             d = con.read(True, callback=callback)

        #             if not d:
        #                 return con.data(True)

        #         else:
        #             con.read()
        #             return con.data()
        #     except Exception as e:
        #         continue
        # raise TimeoutError("can not connect to ")
        con = socket(AF_INET, SOCK_DGRAM)
        con.settimeout(10)
        try:
            con.sendto(msg, (self.ip, self.port))
            d = con.recvfrom(int(65534/2))[0]
            if callback:
                return callback(d)
            return d
        except TimeoutError as e:
            log.error("Udp Timeout !")
        except Exception as e:
            log.error(e)
            raise e


    def check(self):
        return self.sendto("", op='check')

    def install(self):
        return self.sendto("", op='base')

    def reload(self, main=True):
        if main:
            b = Bitter(self.ip, UDP_PORT_BAK)
            return b.sendto("main", op='reinstall')
        else:
            return self.sendto("bak", op="reinstall")


    def sendto(self, msg, id=None, op="msg", decoder='', callback=None):
        if not id:
            for f in os.listdir(pubip_rsa.home):
                if f.startswith(self.ip):
                    id = f.split(".pub")[0].strip()
                    log.info("Found server's Pub key: " + id)
                    break

        msg = Format(msg, op=op, id=id, decoder=decoder)
        log.debug("sending...")
        rec = None
        try:
            rec = self._sock_send(msg, callback=callback)
        except TimeoutError:
            log.error("no recev ! [timeout]")
            return rec
        log.debug("send [ok]")
        if rec:
            log.debug("recv : " + str(rec))
        else:
            return None
        res = deFormat(rec)
        return res

    def onlysend(self, msg, id=None, op="msg", decoder='', callback=None, loop=None, policy=None):
        if not id:
            for f in os.listdir(pubip_rsa.home):
                if f.startswith(self.ip):
                    id = f.split(".pub")[0].strip()
                    log.info("Found server's Pub key: " + id)
                    break
        msg = Format(msg, op=op, id=id, decoder=decoder)
        self.con = Connection(self.ip, self.port,'udp',double_route=True, policy=policy, loop=loop)
        self.con.write(msg)
        if callback:
            self.con.read(callback=callback)

    def _async_read_patch(self, callback):
        def __async_read_patch(rec):
            if rec:
                res = deFormat(rec)
                if 'result' in res:
                    if 'pickle' in res['result'] and res['result']['pickle']:
                        o = pickle.loads(base64.b64decode(res['result']))
                        if isinstance(o, Exception):
                            raise o
                        res['result'] = o
                callback(res)
            else:
                if hasattr(self, "con"):
                    log.error(getattr(self,"con").log())
                raise Exception(self.ip + ":No back Error ")
        return __async_read_patch

    def async_send(self, msg, callback, id=None, op='msg', decoder='', loop=None, policy=None):
        read_callback = self._async_read_patch(callback)
        self.onlysend(msg, id=id, op=op, decoder=decoder, callback=read_callback,loop=loop, policy=policy)


    def register(self):
        k = pubip_rsa.export_key()
        self.onlysend(k, op='reg', decoder='base64', callback=self._regist_read)

    def _regist_read(self, rec):
        res = deFormat(rec)
        try:
            pubip_rsa.import_key(res['msg'])
            c = Cache(DB_PATH)
            reg = Reg(host=self.ip)
            reg.save(c)
            del c
        except Exception as e:
            print(e)


    def regist_to_server(self):
        k = pubip_rsa.export_key()
        try:
            res = self.sendto(k, op='reg', decoder='base64')
            log.error(res)
            pubip_rsa.import_key(res['msg'])
            c = Cache(DB_PATH)
            reg = Reg(host=self.ip)
            reg.save(c)
            del c
        except Exception as e:
            print(e)
            return if_rsa


class Bitters:

    def __init__(self):
        self.hs = set()
        self.op = 'circle'
        self._how_to_use_var = 'every'
        self.failed = []
        self.callback = print

    def how_to_use_var(self, kind='every'):
        """
            kind: 'every/each'
            @every: will run like : [ func(i) for i in args]
            @each: will run like:  [func(args) for i in all_hosts]
        """
        self._how_to_use_var = kind


    def filter(self, key):
        hosts_db = Cache(DB_PATH)
        for host in hosts_db.query(Host):
            if key in host.host:
                self.hs.add(host.host)


    def __getattr__(self, func_name):

        def _rpc(*args, **kwargs):
            R = []
            if len(self.hs) == 0:
                self.filter(".")
            if self._how_to_use_var == 'every':
                hs = list(self.hs)
                l = len(self.hs)
                for i,k in enumerate(args):
                    h = hs[i % l]
                    b = Bitter(h, async_rpc=True)
                    b.op = self.op
                    b.callback = self.callback
                    try:
                        res =  getattr(b, func_name)(k, **kargs)
                        R.append(res)
                    except Exception as e:
                        self.failed.append([h,e])

            elif self._how_to_use_var == 'each':
                for h in self.hs:
                    b = Bitter(h, async_rpc=True)
                    b.op = self.op
                    b.callback = self.callback
                    call =  getattr(b, func_name)
                    try:
                        res = call(*args, **kwargs)
                        R.append(res)
                    except Exception as e:
                        self.failed.append([h,e])
            return R
        return _rpc



class DaemonSeed(Daemon):

    def run(self):
        serv = UDPServer(('0.0.0.0', UDP_PORT), DaemonServer)
        log.info("Start server: {}".format(UDP_PORT))
        serv.serve_forever()

class DaemonSeedBak(Daemon):
    def run(self):
        serv = UDPServer(('0.0.0.0', UDP_PORT_BAK), DaemonServer)
        log.info("Start bak server: {}".format(UDP_PORT_BAK))
        serv.serve_forever()


def test_key_reg(ip):
    b = Bitter(ip)
    k = pubip_rsa.export_key()
    return b.sendto(k, op='reg')

def main():
    app = DaemonSeed("/tmp/seed.pid")
    if len(sys.argv) < 2:
        log.error("need 'start' or 'stop'")
        sys.exit(0)
    if sys.argv[1] == 'start':
        app.start()
    elif sys.argv[1] == 'stop':
        app.stop()

def main_start_bak():

    app = DaemonSeed("/tmp/seed_bak.pid")
    if len(sys.argv) < 2:
        log.error("need 'start' or 'stop'")
        sys.exit(0)
    if sys.argv[1] == 'start':
        app.start()
    elif sys.argv[1] == 'stop':
        app.stop()

if __name__ == "__main__":
    app = DaemonSeed("/tmp/seed.pid")
    if len(sys.argv) < 2:
        s = UDPServer(('0.0.0.0', UDP_PORT), DaemonServer)
        log.info("Start server: {}".format(UDP_PORT))
        s.serve_forever()
    else:
        if sys.argv[1] == 'start':
            app.start()
        else:
            app.stop()
