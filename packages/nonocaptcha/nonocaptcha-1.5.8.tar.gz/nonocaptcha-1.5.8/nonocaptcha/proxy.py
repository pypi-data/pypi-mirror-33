import time
from pprint import pprint

class Proxy(object):
    def __init__(self, proxy):
        self.proxy = proxy
        self.banned = False
        self.in_use = False
        self.last_used = 0

proxies = """5.79.87.139:46424
46.165.249.167:35150
94.242.252.103:42649
94.242.252.102:41402
190.2.137.20:34022
78.31.67.206:45442
5.79.87.139:44199
85.17.193.210:37538
37.48.81.151:46118
213.202.254.161:34175""".split()

proxies = set(Proxy(proxy) for proxy in proxies)
order_to_use = iter(sorted((p for p in proxies if not p.in_use), key=lambda x: x.last_used))
proxy = next(order_to_use)
proxy.in_use = True
# do something
proxy.last_used = time.time()

