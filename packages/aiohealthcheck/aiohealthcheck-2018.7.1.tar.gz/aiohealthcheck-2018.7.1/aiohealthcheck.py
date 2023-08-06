""" aiohealthcheck: super-simple TCP health-check endpoint

   Copyright 2017 Caleb Hattingh

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""


__version__ = '2018.7.1'


import logging
import asyncio
from asyncio import StreamReader, StreamWriter
from typing import Callable


logger = logging.getLogger(__name__)


async def tcp_health_endpoint(
        port: int = 5000,
        host: str = '0.0.0.0',
        payload: Callable[[], str] = lambda: 'ping'):

    async def connection(reader: StreamReader, writer: StreamWriter):
        try:
            writer.write(payload().encode())
            await writer.drain()
            writer.close()
        except:  # pragma: no cover
            logger.exception('Error in health-check:')

    logger.info('Starting up the health-check listener on %s:%s', host, port)
    server = await asyncio.start_server(connection, host=host, port=port)

    try:
        # Wait around till this coroutine is cancelled.
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.warning('Shutting down the health check listener.')
        server.close()
        await server.wait_closed()

