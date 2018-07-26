from asyncio import *
proc = create_subprocess_exec


def run(coro):
    # stole the idea from 3.7
    loop = get_event_loop()
    return loop.run_until_complete(coro)


def spawn(coro):
    # also again stole the idea from 3.7
    return get_event_loop().create_task(coro)
