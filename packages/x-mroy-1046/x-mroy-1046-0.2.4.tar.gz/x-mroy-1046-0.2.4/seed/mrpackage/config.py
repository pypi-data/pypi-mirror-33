from qlib.data import Cache, dbobj
from fabric.api import env
import os
import logging
import sys
if sys.platform.startswith("win"):
     print("Not support Win")
     sys.exit(0)

Join = os.path.join
Exists = os.path.exists

LOG_LEVEL = logging.INFO
SEED_HOME = os.path.join(os.getenv("HOME"), ".config/seed")

LOG_CONFIG_PATH = Join(SEED_HOME, "log_config")
MODULE_PATH = Join(SEED_HOME, "scripts")
STATUS_PATH = Join(SEED_HOME, "status")

if not Exists(Join(os.getenv("HOME"), ".config")):
     os.mkdir("/root/.config")

if not os.path.exists(SEED_HOME):
     os.mkdir(SEED_HOME)

if not os.path.exists(MODULE_PATH):
     os.mkdir(MODULE_PATH)


if os.getenv("DEBUG"):
     s = os.getenv("DEBUG").strip()
     if hasattr(logging, s):
          LOG_LEVEL = getattr(logging, s)
     else:
          DEBUG = True
          LOG_LEVEL = logging.INFO

if os.path.exists(LOG_CONFIG_PATH):
     with open(Join(SEED_HOME, "log_config")) as fp:
          l = fp.read().strip()
          if hasattr(logging, l):
               LOG_LEVEL = getattr(logging, l)

SEED_HOME = os.path.join(os.getenv("HOME"), ".config/seed")
if not os.path.exists(SEED_HOME):
     os.mkdir(SEED_HOME)

LOCAL_PUB_KEY = os.getenv("HOME") + "/.ssh/id_rsa.pub"

DB_PATH = os.path.join(SEED_HOME, 'cache.db')


class Host(dbobj):
     def patch(self):
         global env
         env.passwords[self.user + "@" + self.host + ":" + self.port] = self.passwd
         if self.host not in env.hosts:
             env.hosts.append(self.user + "@" + self.host+ ":" + self.port)

     def display(self):
         print(self.user + "@" + self.host + ":" + self.port + " ---> " + self.passwd)
