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

import json
import logging

import pytest

from gordon_introspection import __version__
from gordon_introspection import app


@pytest.fixture
def server_app(config):
    return app.ServerApp(config)


# loop fixture is from aiohttp, not to be confused with pytest-asyncio's
# event_loop fixture
async def test_ping(aiohttp_client, loop, server_app):
    """Request /ping healthcheck endpoint."""
    client = await aiohttp_client(server_app.app)
    resp = await client.get('/ping')
    assert 200 == resp.status
    text = await resp.text()
    assert 'pong' == text


async def test_version(aiohttp_client, loop, server_app):
    """Request /version metadata endpoint."""
    client = await aiohttp_client(server_app.app)
    resp = await client.get('/version')
    assert 200 == resp.status
    resp = json.loads(await resp.text())
    assert __version__ == resp['gordon-introspection']


async def test_system(aiohttp_client, loop, server_app, mocker):
    """Request /system metadata endpoint."""
    client = await aiohttp_client(server_app.app)
    resp = await client.get('/system')
    assert 200 == resp.status
    resp = json.loads(await resp.text())
    assert 'uptime' in resp
    assert 'system_time' in resp


@pytest.fixture
def loggers(monkeypatch):
    loggers = {
        'testing1': logging.getLogger('testing1'),
        'testing2': logging.getLogger('testing2'),
        'testing3': logging.PlaceHolder(logging.getLogger('placeholder')),
    }
    loggers['testing1'].setLevel('INFO')
    loggers['testing2'].setLevel('DEBUG')
    monkeypatch.setattr(
        'gordon_introspection.views.logging.Logger.manager.loggerDict', loggers)
    return loggers


@pytest.mark.parametrize('req,exp_status,exp_body', (
    ('', 200, json.dumps({'testing1': 'INFO', 'testing2': 'DEBUG'})),
    ('?logger=testing1', 200, json.dumps({'testing1': 'INFO'})),
    ('?logger=testing3', 400, '400: "testing3" is a PlaceHolder object.'),
    ('?logger=notalogger', 404, '404: Unknown logger: "notalogger".')
))
async def test_get_log_state(req, exp_status, exp_body, loggers,
                             aiohttp_client, loop, server_app):
    """Request /logging endpoint."""
    client = await aiohttp_client(server_app.app)
    resp = await client.get(f'/logging{req}')
    assert exp_status == resp.status
    text = await resp.text()
    assert exp_body == text


@pytest.mark.parametrize('req,exp_status,exp_body', (
    ('', 400, '400: Query parameters "logger" and "level" are required.'),
    ('?logger=testing1', 400,
        '400: Query parameters "logger" and "level" are required.'),
    ('?level=INFO', 400,
        '400: Query parameters "logger" and "level" are required.'),
    ('?logger=notalogger&level=WARN', 404,
        '404: Unknown logger: "notalogger".'),
    ('?logger=testing1&level=FUU', 404, '404: Unknown log level: "FUU".'),
    ('?logger=testing1&level=DEBUG', 204, ''),
))
async def test_set_log_state(req, exp_status, exp_body, loggers,
                             aiohttp_client, loop, server_app):
    """Update logger level via /logging?logger=NAME&level=LEVEL."""
    client = await aiohttp_client(server_app.app)
    resp = await client.post(f'/logging{req}')
    assert exp_status == resp.status
    text = await resp.text()
    assert exp_body == text


async def test_set_log_state_fails(monkeypatch, loggers, aiohttp_client, loop,
                                   server_app):
    """Level could not be updated."""
    monkeypatch.setattr(
        'gordon_introspection.views.logging.getLevelName', lambda x: 'ERROR')

    client = await aiohttp_client(server_app.app)
    resp = await client.post('/logging?logger=testing1&level=INFO')
    assert 500 == resp.status
    text = await resp.text()
    assert f'500: Could not update log level of "testing1" to "INFO".' == text
