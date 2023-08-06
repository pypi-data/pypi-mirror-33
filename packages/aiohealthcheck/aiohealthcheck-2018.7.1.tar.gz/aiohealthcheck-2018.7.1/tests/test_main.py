import asyncio
from contextlib import suppress

import aiohealthcheck


def test_health(loop: asyncio.AbstractEventLoop):

    results = []
    PORT = 5000
    COUNT = 10

    async def dummy_k8s():
        # Wait for server to be up
        await asyncio.sleep(0.5)

        for i in range(COUNT):
            reader, writer = await asyncio.open_connection(
                host='localhost', port=PORT, loop=loop
            )
            results.append(await reader.read(1024))
            writer.close()
            del reader
            del writer
            print('.', end='', flush=True)

    t1 = loop.create_task(aiohealthcheck.tcp_health_endpoint(PORT))
    t2 = loop.create_task(dummy_k8s())

    try:
        loop.run_until_complete(asyncio.wait_for(t2, 50))
    finally:
        assert results == [b'ping'] * COUNT
        group = asyncio.gather(t1, t2, return_exceptions=True)
        group.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(group)
