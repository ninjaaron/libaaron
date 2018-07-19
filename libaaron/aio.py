import asyncio
sleep = asyncio.sleep
proc = asyncio.create_subprocess_exec


def run(coro):
    # stole the idea from 3.7
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


async def spawn(coro):
    # also again stole the idea from 3.7
    return asyncio.get_event_loop().create_task(coro)
