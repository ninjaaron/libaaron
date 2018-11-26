import sys
from asyncio import *

proc = create_subprocess_exec
major, minor, *_ = sys.version_info

if (major, minor) < (3, 7):

    def run(coro):
        loop = get_event_loop()
        return loop.run_until_complete(coro)

    def create_task(coro):
        return get_event_loop().create_task(coro)
