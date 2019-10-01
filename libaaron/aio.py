import sys
from asyncio import *
proc = create_subprocess_exec

if sys.version_info < (3, 7, 0):

    def run(coro):
        loop = get_event_loop()
        return loop.run_until_complete(coro)

    create_task = ensure_future
