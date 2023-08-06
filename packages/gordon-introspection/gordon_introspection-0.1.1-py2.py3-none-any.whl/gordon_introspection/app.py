# -*- coding: utf-8 -*-
#
# Copyright 2018 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Main module to run the Gordon introspection server.

.. attention::
    The event consumer client is an internal module for the core gordon
    logic. No other use cases are expected.
"""

import logging

import attr
import zope.interface
from aiohttp import web
from gordon import interfaces

from gordon_introspection import views


@attr.s
class ServerConfig:
    """Gordon server configuration."""
    raw = attr.ib(factory=dict)
    host = attr.ib(init=False)
    port = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.host = self.raw.get('host', '0.0.0.0')
        self.port = self.raw.get('port', 8080)


@zope.interface.implementer(interfaces.IRunnable)
class ServerApp:
    """Entrypoint to the Gordon introspection server application.

    Args:
        config (dict): Server-plugin-specific configuration. See
            :doc:`config` for more information.
    """
    def __init__(self, config, **kwargs):
        self.config = ServerConfig(config)
        self.app = web.Application()
        self._setup_routes()
        self._runner = web.AppRunner(self.app)

    def _setup_routes(self):
        self.app.add_routes(views.routes)

    async def run(self):
        """Start the Gordon introspection server."""
        msg = f'Starting server on {self.config.host}:{self.config.port}...'
        logging.info(msg)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.config.host, self.config.port)
        await site.start()

    async def shutdown(self):
        """Gracefully stop the runner running the server app."""
        msg = f'Stopping server...'
        logging.info(msg)
        await self._runner.cleanup()
        msg = f'Successfully stopped Gordon Introspection server.'
        logging.info(msg)
