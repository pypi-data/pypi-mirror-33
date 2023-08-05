import os
import zlib
import subprocess
import base64
import json
import time

from seed.mrpackage.libs import log
from seed.mrpackage.config import STATUS_PATH

class FileHandle:
    def __init__(self, name=None, b64=False):
        self.name = name
        self.b64 = b64

    def pack(self, file):
        data = None
        name = None
        path = None
        if os.path.exists(file):
            path = os.path.dirname(file).encode("utf8")
            name = os.path.basename(file).encode("utf8")
            nl = len(name)
            pl = len(path)
            with open(file, 'rb') as fp:
                data = zlib.compress(fp.read())
            dl = len(data)
            h = nl.to_bytes(2,'big') + pl.to_bytes(2, 'big') + dl.to_bytes(2, 'big') + name + path
            D = h + data
            if self.b64:
                return base64.b64encode(D)
            return D

    def unpack(self, data):
        if self.b64:
            data = base64.b64decode(data)
        nl = int.from_bytes(data[0:2], 'big')
        pl = int.from_bytes(data[2:4], 'big')
        dl = int.from_bytes(data[4:6], 'big')
        name = data[6:nl + 6]
        path = data[nl+6:nl+pl+6]
        d = data[nl+pl+6:]
        if len(d) != dl:
            raise Exception("data error")
        data = zlib.decompress(d)
        return name, path, data


class Os:

    def __init__(self, log='/tmp/seed-control.log'):
        self.Init()
        self.log = log
        self.mdeal = ' | while IFS= read -r line; do printf \'[%s] %s\n\' "$(date \'+%Y-%m-%d %H:%M:%S\')" "$line"; done '
        if hasattr(self, 'Setup'):
            getattr(self, 'Setup')()

    def Init(self):
        ps = os.listdir("/usr/bin/")
        if 'apt' in ps:
            self.o = 'u'
            self.installer = 'apt install -y '
            self.installer_u = 'apt update '
            self.uninstall = 'apt remove -y '
        elif 'yum' in ps:
            self.o = 'c'
            self.installer = 'yum install -y '
            self.installer_u = 'yum update'
            self.uninstall = 'yum remove -y '
        else:
            self.o = 'c'
            self.installer = 'apt-get install -y '
            self.installer_u = 'apt-get update '
        self.pip = 'pip3 install  '
        self.pip_u = 'pip3 upgrade '
        self.unpip = 'pip3 uninstall -y '
        #if self.check('pip'):
        #    self.pip2 = 'pip'


    def generate_ssh_key(self, args):
        self.Run("mkdir -p /root/.ssh/")
        self.Run("ssh-keygen -t rsa -P '' -f /root/.ssh/id_rsa")

    def get_pid(self):
        name = self.__class__.__name__.lower()
        subprocess.check_output("ps aux | grep " + name)

    def Install(self, package):
        log.info("try to install " + package)
        os.popen(self.installer + package + self.mdeal + " >> " + self.log).read()

    def Pip(self, package):
        os.popen(self.pip + package + self.mdeal +  " >> " + self.log).read()

    def test(self, args):
        self.Run('whoami')

    def check(self, cmd):
        try:
            stat = subprocess.check_call(['which', cmd])
            if stat == 0:
                return True
            return False
        except Exception:
            return False

    def Run(self, cmd):
        os.popen(cmd +  self.mdeal + ' >> ' + self.log)

    def Uninstall(self, package):
        os.popen(self.uninstall + package + self.mdeal + " >> " + self.log).read()

    def Unpip(self, package):
        os.popen(self.unpip + package + self.mdeal + " >> " + self.log).read()


    def Upload(self, args, dest=None):
        try:
            filehandle = FileHandle(b64=True)
            raw, to = args.split("::")
            name , _, da = filehandle.unpack(raw)
            name = name.decode("utf8")
            if os.path.exists(to):
                des = os.path.join(to, name)
            else:
                des = os.path.join('/tmp', name)
            if dest != None:
                des = dest

            with open(des, 'wb') as fp:
                fp.write(da)
            self.Run('file ' + des)
        except Exception as e:
            self.Run("file upload failed")


    def stdout(self, line):
        try:
            if isinstance(line, bytes):
                line = line.decode("utf8")
            return subprocess.check_output(["tail","-n "+line, self.log])
        except Exception as e:
            return str(e)

    def Update(self, args):
        self.Run(self.installer_u)

    def List(self):
        return [ i for i in self.__dir__() if not i.startswith("_")]

    def Startup(self, args):
        if hasattr(self, "start_command"):
            self.Run(getattr(self, "start_command"))
        else:
            raise Exception("not found start_command for: " + self.__class__.__name__)

    def Status(self):
        return subprocess.check_output(['service', self.__class__.__name__.lower(), 'status'])

    def Check(self, args):
        name = self.__class__.__name__.lower()
        try:
            subprocess.check_call(['hash', name])
            return True
        except subprocess.CalledProcessError as e:
            return False

    def wait(self, cmd, timeout=300):
        s = time.time()
        while not self.check(cmd):
            e = time.time() - s
            time.sleep(1)
            if e > 300:
                break

    def Start(self):
        if hasattr(self , "start_command"):
            self.Run(getattr(self, "start_command"))


class Tor(Os):

    def Setup(self):
        cmd = """
Socks5Proxy  127.0.0.1:1080
SocksPort 3080
ExcludeNodes {cn},{hk},{mo},{sg},{th},{pk},{by},{ru},{ir},{vn},{ph},{my},{cu},{br},{kz},{kw},{lk},{ci},{tk},{tw},{??}
ExcludeExitNodes {cn},{hk},{mo},{sg},{th},{pk},{by},{ru},{ir},{vn},{ph},{my},{cu},{br},{kz},{kw},{lk},{ci},{tk},{tw},{??}
ExitNodes {de}"""
        if not self.check("tor"):
            self.Install('tor')
            if not os.path.exists("/etc/tor"):
                os.mkdir("/etc/tor")
            with open("/etc/tor/torrc", "w") as fp:
                fp.write(cmd)

        if not os.path.exists("/etc/tor/torrc"):
            if not os.path.exists("/etc/tor"):
                 os.mkdir("/etc/tor")
            with open("/etc/tor/torrc", "w") as fp:
                 fp.write(cmd)
        self.start_command = "service tor start"

    def Config(self, args):
        r = open("/etc/tor/torrc").read()
        return r

    def Upload(self, args):
        super().Upload(args, dest="/etc/tor")

    def Proxy(self, args):
        port = int(args)
        self.Run("sed -ie 's/Socks5Proxy .+/Socks5Proxy 127.0.0.1:{port}/g' /etc/tor/torrc".format(port=port))

    def ChangePort(self, args):
        port = int(args)
        self.Run("sed -ie 's/SocksPort .+/SocksPort {port}/g' /etc/tor/torrc".format(port=port))

    def Restart(self, args):
        self.Run("service tor restart")

class Proxychains(Os):

    def Setup(self):
        self.config_path = "/etc/proxychains.conf"
        if not os.path.exists(self.config_path) and os.path.exists("/usr/local/etc/proxychains.conf"):
            self.config_path = "/usr/local/etc/proxychains.conf"

        if not self.check("proxychains4") and not self.check("proxychains"):
            if self.o == 'c':
                cmd = """
yum install -y git
cd /usr/local/src
git clone https://github.com/rofl0r/proxychains-ng.git
cd proxychains-ng
./configure && make && make install
make install-config"""
                with open("/tmp/proxy-install.sh", 'w') as fp: fp.write(cmd)
                os.popen("sh /tmp/proxy-install.sh").read()
                log.info("install proxychains")
                if not os.path.exists(self.config_path):
                    if os.path.exists("/usr/local/etc/proxychains.conf"):
                        self.config_path = "/usr/local/etc/proxychains.conf"

            else:
                self.Install("proxychains")
            self.Run("sed -ie 's/#quiet/quiet/g' " + self.config_path)
        if self.check("proxychains4") and not self.check("proxychains"):
            self.Run("ln -s  /usr/local/bin/proxychains4 /usr/local/bin/proxychains")
            print("create link for proxychains4 --> proxychains")

    def Upload(self, args):
        super().Upload(args, dest=self.config_path)

    def Config(self, args):
        return open(self.config_path).read()

    def ChangePort(self, args):
        port = int(args)
        self.Run("sed -ie 's/^socks5 127.*/socks5 127.0.0.1 {port}/g' {config}".format(port=port, config=self.config_path))


class Shadowsocks(Os):

    def Setup(self):
        if not self.check("sslocal"):
            self.Pip("shadowsocks")
        self.start_command = "ssserver -c /etc/shadowsocks.json -d start"
        self.restart_command = "ssserver -c /etc/shadowsocks.json -d restart"
        self.stop_command = "ssserver -c /etc/shadowsocks.json -d stop"
        self.server_config = {
            "server":"0.0.0.0",
            "port_password": {
                "13001": "thefoolish1",
                "13002": "thefoolish2",
                "13003": "thefoolish3",
                "13004": "thefoolish4",
                "13005": "thefoolish5",
                "13006": "thefoolish6",
                "13007": "thefoolish7",
                "13008": "thefoolish8",
                "13009": "thefoolish9",
                "13010": "thefoolish10",
                "13011": "thefoolish11",
                "13012": "thefoolish12",
                "13013": "thefoolish13"
            },
            "workers": 4,
            "method":"aes-256-cfb"
        }
        self.local_config = {
            "server": "",
            "server_port":13003,
            "password": "thefoolish3",
            "method" : "aes-256-cfb",
            "local_port": 1080,
            "timeout":300
        }

    def Config(self, args):
        if args == 'local':
            return self.local_config
        return self.server_config

    def UpdateConfig(self, args):
        self.Upload(args, dest="/etc/shadowsocks.json")

    def Connect(self, server_ip):
        self.local_config['server'] = server_ip
        with open("/tmp/shadowsocks.json", "w") as fp:
            json.dump(self.local_config, fp)
        self.Run('sslocal -c /tmp/shadowsocks.json -d start')
        self.Run("ps aux | grep sslocal | grep -v 'grep' | awk '{print $2}' | xargs > /tmp/pids/shadowsocks_local.pid")

    def Start(self, args, server_ip=None):
        if args == 'local':
            self.Connect(server_ip)
            return
        elif args == 'server':
            with open("/etc/shadowsocks.json", "w") as fp:
                json.dump(self.server_config, fp)
                self.Run(self.start_command)
            os.popen("ps aux | grep ssserver | awk '{print $2}' |xargs > /tmp/pids/shadowsocks_server_pid ").read()

    def Stop(self, args):
        if args == 'local':
            os.popen("sslocal -c /tmp/shadowskcs.json  -d stop").read()
        elif args == 'server':
            os.popen(self.stop_command).read()


    def Restart(self):
        self.Run(self.restart_command)


class ProxyCircle:

    def __init__(self):
        self.status_file = STATUS_PATH
        if not os.path.exists(self.status_file):
            with open(self.status_file, 'w') as fp:
                fp.write('build')
                self.setup()


    def setup(self):
        self.shadowsocks = Shadowsocks()
        self.shadowsocks.Setup()
        self.tor = Tor()
        self.tor.Setup()
        self.proxychains = Proxychains()
        self.proxychains.Setup()
        self.tor.Proxy(1080)
        self.tor.ChangePort(3080)
        self.proxychains.ChangePort(3080)

        self.forward_pid = False
        self.socks5_pid = False
        self.register_service = []
        if not os.path.exists("/tmp/pids"):
            os.mkdir('/tmp/pids')
        self.register_service =  os.listdir("/tmp/pids")

    def List(self):
        return [ i for i in self.__dir__() if not i.startswith("_")]

    def Netstat(self):
        Lis = os.popen("netstat -tulpn | grep LISTEN | awk '{ print $4 , $7}'").read().split("\n")
        res = []
        for i in Lis:
            if i:
                addr, pi = i.split()
                pid, pro = pi.split("/")
                res.append({"pid":pid, "name":pro, "address":addr})
        # log.error(res)
        return {"data": res}

    def Run(self, cmd):
        log.info("[Cmd]: " + cmd)
        return os.popen(cmd)

    def Shadowsocks(self):
        self.shadowsocks.Start("server")
        self.Run("ps aux | grep ssserver |grep -v 'grep' | awk '{print $2 }' | xargs > /tmp/pids/shadowsocks_server.pid")

    def Socks5Proxy(self, medial_server, exit_server):
        if not ":" in exit_server:
            return "Not correct exit_serer ip should xx.x.x.x:xxx"
        self.exit_server,port = exit_server.split(":")
        self.medial_server = medial_server
        self.shadowsocks.Connect(medial_server)
        self.Run('proxychains ssh -o "StrictHostKeyChecking no"  -fCnND {port} root@{exit_server}'.format(port=port, exit_server=self.exit_server))
        self.socks5_pid =  os.popen("ps aux | grep ssh | grep fCnND | grep -v 'grep' | awk '{print $2}' |xargs > /tmp/pids/socks5.pid").read().strip()

    def PortMap(self, dest, sshport='22', if_tor=False):
        lport, rhost, rport = dest.split(":")
        pre = ''
        if if_tor:
            pre = 'proxychains'
        cmd = '{if_tor} ssh -o "StrictHostKeyChecking no"  -p {sshport} -L 0.0.0.0:{lport}:{rhost}:{rport} root@{rhost} -CnfN'.format(sshport=sshport, lport=lport, rhost=rhost, rport=rport, if_tor=pre)
        self.Run(cmd)
        return os.popen("ps aux | grep ssh | grep CnfN | grep -v 'grep' | awk '{print $2}' |xargs > /tmp/pids/forward.pid ").read().strip()

    def Stop(self, service):
        if service in self.register_service:
            self.Run("cat /tmp/pids/{} | xargs kill -9 ".format(service))
            return "find and kill it"

    def GetStatus(self):
        socks5_pid = -1
        forward_pid = os.popen("ps aux | grep ssh | grep CnfN | grep -v 'grep' | awk '{print $2}' | xargs ").read().strip().split()
        socks5_pid = os.popen("ps aux | grep ssh | grep fCnND  | grep -v 'grep' | awk '{print $2}'  | xargs ").read().strip().split()
        shadowsocks_server_pid = os.popen("ps aux | grep 'ssserver' | grep -v 'grep' | awk '{print $2}' | xargs ").read().strip().split()
        shadowsocks_local_pid = os.popen("ps aux | grep 'sslocal' | grep -v 'grep' | awk '{print $2}' | xargs ").read().strip().split()
        tor_pid = os.popen("ps aux | grep /bin/tor | grep -v 'grep' | awk '{print $2}' | xargs ").read().strip()

        return {
            'socks5' : socks5_pid,
            'shadowsocks_server': shadowsocks_server_pid,
            'shadowsocks_local': shadowsocks_local_pid,
            'forward' : forward_pid,
            'tor': tor_pid,
        }

    def Platform(self):
        return {
            'platform': self.o,
        }

    def Stop(self, args):
        if args ==  'socks5':
            with open("/tmp/socks5.pid") as fp:
                s = fp.read().strip().split()
                for i in s:
                    os.popen("kill -9 {}".format(i))
            os.remove("/tmp/socks5.pid")
        else:
            with open("/tmp/ssh_ford.pid") as fp:
                s = fp.read().strip().split()
                for i in s:
                    os.popen("kill -9 {}".format(i))
            os.remove("/tmp/ssh_ford.pid")

class Module:

    def _run(self,cmd, wait=False):
        log.info("[cmd]:" + cmd)
        c = cmd + " 1>/tmp/module.log 2>/tmp/module.error.log"
        if wait:
            os.popen(c).read()
        else:
            os.popen(c)

    def Install(self):
        self._run(self.install, True)

    def Check(self):
        for cmd in self.names:
            try:
                stat = subprocess.check_call(['which', cmd])
                if stat == 0:
                    return True
            except Exception:
                pass
        return False
