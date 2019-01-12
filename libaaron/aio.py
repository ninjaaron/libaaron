import sys
from asyncio import *

proc = create_subprocess_exec
major, minor, *_ = sys.version_info

if (major, minor) < (3, 7):

    def run(coro):
        loop = get_event_loop()
        return loop.run_until_complete(coro)

    create_task = ensure_future
