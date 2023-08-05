import os
import socket
import asyncio
import time
import async_timeout
from seed.mrpackage.config import SEED_HOME, DB_PATH, Host, Cache
from seed.mrpackage.udp import open_remote_endpoint
from seed.mrpackage.libs import loger

log = loger()

async def check_up(ip, loop, msg='-v'):
    try:
        handler = await open_remote_endpoint(ip,60077)
    except Exception as e:
        return ip, False, e
    try:
        re = handler.send(msg.encode('utf8'))
        recevier = handler.receive()
        res = await asyncio.wait_for(recevier, timeout=10)
    except asyncio.TimeoutError as e:
        return ip, False, e
    log.info("[check ok] :" + ip + " : "+  time.asctime())
    return ip,True,'good'

async def _run(loop,ips, msg='-v'):
    tasks = [check_up(ip, loop, msg=msg) for ip in ips]
    return await asyncio.gather(*tasks)

class Test:
    def __init__(self):
        ca = Cache(DB_PATH)
        self.ips  = [h.host for h in ca.query(Host)]
        del ca


    def check_hosts(self, msg='-v'):
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        ips = self.ips
        res = loop.run_until_complete(_run(loop, ips, msg=msg))
        loop.close()
        return res
