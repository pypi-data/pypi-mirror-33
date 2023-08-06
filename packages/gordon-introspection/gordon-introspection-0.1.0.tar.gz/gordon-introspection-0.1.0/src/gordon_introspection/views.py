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
"""Defined views/logic for each introspective endpoint.

See :doc:`endpoints` for more information.
"""

import asyncio
import logging
import os
import platform
import sys

import pkg_resources
from aiohttp import web


routes = web.RouteTableDef()


@routes.get('/ping')
async def ping(request):
    """Quick healthcheck for app 'liveness'.

    Endpoint::

        GET /ping

    Returns:
        (:obj:`aiohttp.web.Response`): ``200`` HTTP status code with
            ``pong`` in the body.
    """
    return web.Response(text='pong')


@routes.get('/version')
async def version(request):
    """Get the running version of Gordon and its dependencies.

    Endpoint::

        GET /version

    Returns:
        (:obj:`aiohttp.web.json_response`): JSON representation of
            package name to version declared in the package's setup.py,
            i.e. {'gordon-dns': '1.0.0', 'gordon-server': '0.0.1', ...}
    """
    packages = pkg_resources.working_set
    installed = {p.project_name: p.version for p in packages}

    return web.json_response(installed)


async def _get_sh_command_output(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE)
    output = await process.stdout.readline()
    return output.decode('ascii').rstrip()


@routes.get('/system')
async def system(request):
    """Get system-related information.

    Endpoint::

        GET /system

    Returns:
        (:obj:`aiohttp.web.json_response`): JSON representation of
            system-related information.
    """
    uptime = await _get_sh_command_output(cmd='uptime')
    system_time = await _get_sh_command_output(cmd='date')
    pid = os.getpid()
    python_version_info = {
        'version': sys.version,
        'executable': sys.executable,
        'pythonpath': sys.path,
        'version_info': {
            'major': sys.version_info.major,
            'minor': sys.version_info.minor,
            'micro': sys.version_info.micro,
            'releaselevel': sys.version_info.releaselevel,
            'serial': sys.version_info.serial
        }
    }
    operating_system = {
        'platform': sys.platform,
        'name': os.name,
        'uname': platform.uname()
    }

    ret = {
        'uptime': uptime,
        'system_time': system_time,
        'pid': pid,
        'python': python_version_info,
        'os': operating_system,

    }
    return web.json_response(ret)


def _get_one_or_all_loggers(logger_name=None):
    all_loggers = logging.Logger.manager.loggerDict
    valid_loggers = {}
    for name, logger in all_loggers.items():
        if logger_name and logger_name == name:
            if isinstance(logger, logging.PlaceHolder):
                msg = f'"{logger_name}" is a PlaceHolder object.'
                raise web.HTTPBadRequest(reason=msg)
            return logger
        if isinstance(logger, logging.PlaceHolder):
            continue
        valid_loggers[name] = logger
    return valid_loggers


@routes.get('/logging')
async def get_log_state(request):
    """Get logger(s) current level.

    Endpoint::

        GET /logging
        GET /logging?logger=NAME

    If ``logger`` name is not provided in the request, all loggers for
    the application will be returned.

    Args:
        request (aiohttp.web.Request): HTTP request object.

    Returns:
        (:obj:`aiohttp.web.json_response`) JSON representation of
            {'LOGGER': 'LEVEL'}

    Raises:
        (:exc:`aiohttp.web.HTTPNotFound`) Requested logger not found.
        (:exc:`aiohttp.web.HTTPBadRequest`) Requested logger is a
            PlaceHolder logger.
    """
    logger_name = request.query.get('logger')

    # return all
    if logger_name is None:
        loggers = {}
        for k, v in _get_one_or_all_loggers().items():
            loggers[k] = logging.getLevelName(v.level)
        return web.json_response(loggers)

    try:
        logger_name = logger_name.lower()
        target_logger = _get_one_or_all_loggers(logger_name)

        logger_level = logging.getLevelName(target_logger.level)
        return web.json_response({logger_name: logger_level})
    except (KeyError, AttributeError):
        msg = f'Unknown logger: "{logger_name}".'
        raise web.HTTPNotFound(reason=msg)


@routes.post('/logging')
async def set_log_state(req):
    """Set a logger's level.

    Endpoint::

        POST /logging?logger=NAME&level=LEVEL

    Args:
        request (aiohttp.web.Request): HTTP request object.

    Returns:
        (:obj:`aiohttp.web.Response`): ``204`` HTTP status code with
            no content in body.

    Raises:
        (:exc:`aiohttp.web.HTTPNotFound`) Requested logging level not
            found.
        (:exc:`aiohttp.web.HTTPNotFound`) Requested logger not found.
        (:exc:`aiohttp.web.HTTPBadRequest`) Requested logger is a
            PlaceHolder logger.
        (:exc:`aiohttp.web.HTTPInternalServerError`) Logger level could
            not be updated to desired level.
    """
    desired_level = req.query.get('level')
    target_logger = req.query.get('logger')

    if desired_level is None or target_logger is None:
        msg = 'Query parameters "logger" and "level" are required.'
        raise web.HTTPBadRequest(reason=msg)

    desired_level = desired_level.upper()

    valid_levels = (
        'CRITICAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'NOTSET'
    )

    if desired_level not in valid_levels:
        msg = f'Unknown log level: "{desired_level}".'
        raise web.HTTPNotFound(reason=msg)

    logger = _get_one_or_all_loggers(target_logger)

    try:
        if desired_level == 'WARN':
            desired_level = 'WARNING'
        logger.setLevel(desired_level)
    except (ValueError, AttributeError):
        msg = f'Unknown logger: "{target_logger}".'
        raise web.HTTPNotFound(reason=msg)

    updated_level = logging.getLevelName(logger.level)
    if desired_level != updated_level:
        msg = (f'Could not update log level of "{target_logger}" to '
               f'"{desired_level}".')
        logging.error(msg)
        raise web.HTTPInternalServerError(reason=msg)

    return web.Response(status=204)
