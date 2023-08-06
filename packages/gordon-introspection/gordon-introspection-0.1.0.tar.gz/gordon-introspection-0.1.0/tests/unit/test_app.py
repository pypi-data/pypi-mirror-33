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

import pytest
from aiohttp import web

from gordon_introspection import app


@pytest.mark.parametrize('config,expected', (
    ({}, ('0.0.0.0', 8080)),  # default params
    ({'host': '127.1.1.1', 'port': 1234}, ('127.1.1.1', 1234)),
))
def test_server_config(config, expected):
    """Create server config object."""
    server_config = app.ServerConfig(config)

    assert config == server_config.raw
    assert expected[0] == server_config.host
    assert expected[1] == server_config.port


@pytest.fixture
def application(mocker, monkeypatch):
    mock = mocker.Mock(web.Application)
    mock.router = mocker.Mock()
    mock.router.add_get = mocker.Mock(return_value=True)
    monkeypatch.setattr('gordon_introspection.app.web.Application', mock)
    return mock


@pytest.fixture
def runner(mocker, monkeypatch):
    mock = mocker.Mock(web.AppRunner)
    mock.setup.return_value = True
    monkeypatch.setattr('gordon_introspection.app.web.AppRunner', mock)
    return mock


@pytest.fixture
def tcp_site(mocker, monkeypatch):
    mock = mocker.Mock(web.TCPSite)
    monkeypatch.setattr('gordon_introspection.app.web.TCPSite', mock)
    return mock


def test_server_app_init(mocker, config, application, runner):
    """Create server app."""
    server_app = app.ServerApp(config)

    assert '127.0.0.1' == server_app.config.host
    assert 9999 == server_app.config.port

    server_app.app.add_routes.assert_called_once_with(app.views.routes)


@pytest.mark.asyncio
async def test_server_app_run(config, mocker, monkeypatch, runner, tcp_site,
                              caplog):
    """Run server app via a non-blocking runner."""
    server_app = app.ServerApp(config)

    mock_setup_call_count = 0
    mock_setup_call_args = []

    async def setup(*args, **kwargs):
        nonlocal mock_setup_call_count
        nonlocal mock_setup_call_args

        mock_setup_call_count += 1
        mock_setup_call_args.append((args, kwargs))

    mock_start_call_count = 0
    mock_start_call_args = []

    async def start(*args, **kwargs):
        nonlocal mock_start_call_count
        nonlocal mock_start_call_args

        mock_start_call_count += 1
        mock_start_call_args.append((args, kwargs))

    monkeypatch.setattr(runner, 'setup', setup)
    monkeypatch.setattr(tcp_site.return_value, 'start', start)
    monkeypatch.setattr(server_app, '_runner', runner)
    await server_app.run()

    assert 1 == len(caplog.records)
    assert 1 == mock_setup_call_count
    assert 1 == mock_start_call_count

    assert [((), {})] == mock_setup_call_args
    assert [((), {})] == mock_start_call_args


@pytest.mark.asyncio
async def test_server_app_shutdown(config, mocker, monkeypatch, caplog):
    """Stop runner that's running the server app."""
    server_app = app.ServerApp(config)

    runner = mocker.Mock()
    mock_cleanup_call_count = 0
    mock_cleanup_call_args = []

    async def cleanup(*args, **kwargs):
        nonlocal mock_cleanup_call_count
        nonlocal mock_cleanup_call_args

        mock_cleanup_call_count += 1
        mock_cleanup_call_args.append((args, kwargs))

    monkeypatch.setattr(runner, 'cleanup', cleanup)
    monkeypatch.setattr(server_app, '_runner', runner)

    await server_app.shutdown()

    assert 2 == len(caplog.records)
    assert 1 == mock_cleanup_call_count

    assert [((), {})] == mock_cleanup_call_args
