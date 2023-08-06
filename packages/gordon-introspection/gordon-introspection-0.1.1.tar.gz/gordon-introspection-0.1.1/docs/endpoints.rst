Endpoints
=========


Healthchecks
------------

.. http:get:: /ping

    Quick healthcheck for app 'liveness'.

    **Example Request:**

    .. sourcecode:: http

      GET /ping HTTP/1.1
      Host: 0.0.0.0:8080
      Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/plain; charset=utf-8
        Content-Length: 4
        Server: Python/3.6 aiohttp/3.2.1

        pong

    :resheader Content-Type: text/plain
    :status 200: no error


Metadata
--------

.. http:get:: /version

    Get the running version of Gordon and its dependencies.

    **Example Request:**

    .. sourcecode:: http

      GET /version HTTP/1.1
      Host: 0.0.0.0:8080
      Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=utf-8
        Content-Length: 558
        Server: Python/3.6 aiohttp/3.2.1

        {
            "zope.interface": "4.5.0",
            "yarl": "1.2.4",
            "urllib3": "1.22",
            "ulogger": "1.0.1",
            "toml": "0.9.4",
            "six": "1.11.0",
            "setuptools": "28.8.0",
            "requests": "2.18.4",
            "pytest": "3.5.1",
            "pytest-aiohttp": "0.3.0",
            "py": "1.5.3",
            "pluggy": "0.6.0",
            "pip": "10.0.1",
            "multidict": "4.3.1",
            "more-itertools": "4.1.0",
            "idna": "2.6",
            "idna-ssl": "1.0.1",
            "click": "6.7",
            "chardet": "3.0.4",
            "certifi": "2018.4.16",
            "attrs": "18.1.0",
            "async-timeout": "3.0.0",
            "async-dns": "1.0.0",
            "aiohttp": "3.2.1",
            "gordon-dns": "0.0.1.dev1",
            "gordon-introspection": "0.0.1.dev0"
        }

    :resheader Content-Type: application/json
    :status 200: no error


.. http:get:: /system

    Get system-related information.

    **Example Request:**

    .. sourcecode:: http

      GET /system HTTP/1.1
      Host: 0.0.0.0:8080
      Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=utf-8
        Content-Length: 1101
        Server: Python/3.6 aiohttp/3.2.1

        {
          "uptime": "18:05  up 43 days,  4:54, 8 users, load averages: 2.19 1.77 1.69",
          "system_time": "Wed May 30 18:05:45 EDT 2018",
          "pid": 65161,
          "python": {
            "version": "3.6.2 (default, Jul 22 2017, 12:07:11) \n[GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)]",
            "executable": "executable": "/Users/lynn/.pyenv/versions/3.6.2/envs/gordon-introspection-test/bin/python",
            "pythonpath": [
               "/Users/lynn/.pyenv/versions/3.6.2/envs/gordon-introspection-test/bin",
              "/Users/lynn/.pyenv/versions/3.6.2/lib/python36.zip",
              "/Users/lynn/.pyenv/versions/3.6.2/lib/python3.6",
              "/Users/lynn/.pyenv/versions/3.6.2/lib/python3.6/lib-dynload",
              "/Users/lynn/.pyenv/versions/3.6.2/envs/gordon-introspection-test/lib/python3.6/site-packages",
              "/Users/lynn/Dev/spotify/alf/gordon/core",
              "/Users/lynn/Dev/spotify/alf/gordon/server/src"
            ],
            "version_info": {
              "major": 3,
              "minor": 6,
              "micro": 2,
              "releaselevel": "final",
              "serial": 0
            }
          },
          "os": {
            "platform": "darwin",
            "name": "posix",
            "uname": [
              "Darwin",
              "nope.local",
              "16.7.0",
              "Darwin Kernel Version 16.7.0: Wed Oct  4 00:17:00 PDT 2017; root:xnu-3789.71.6~1/RELEASE_X86_64",
              "x86_64",
              "i386"
            ]
          }
        }

    :resheader Content-Type: application/json
    :status 200: no error


Logging
-------

.. http:get:: /logging

    Get all loggers.

    **Example Request:**

    .. sourcecode:: http

      GET /logging HTTP/1.1
      Host: 0.0.0.0:8080
      Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=utf-8
        Content-Length: 223
        Server: Python/3.6 aiohttp/3.2.1

        {
            "concurrent.futures": "NOTSET",
            "asyncio": "NOTSET",
            "aiohttp.access": "NOTSET",
            "aiohttp.client": "NOTSET",
            "aiohttp.internal": "NOTSET",
            "aiohttp.server": "NOTSET",
            "aiohttp.web": "NOTSET",
            "aiohttp.websocket": "NOTSET"
        }

    :resheader Content-Type: application/json
    :status 200: no error


.. http:get:: /logging?logger=$NAME

    Get one logger.

    **Example Request:**

    .. sourcecode:: http

      GET /logging?logger=asyncio HTTP/1.1
      Host: 0.0.0.0:8080
      Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=utf-8
        Content-Length: 21
        Server: Python/3.6 aiohttp/3.2.1

        {"asyncio": "NOTSET"}

    :query logger: target logger
    :resheader Content-Type: application/json
    :status 200: no error
    :status 400: requested logger is a :obj:`logging.PlaceHolder`
    :status 404: logger not found


.. http:post:: /logging

    Set a logger's level.

    **Example Request:**

    .. sourcecode:: http

      POST /logging?logger=asyncio&level=INFO HTTP/1.1
      Host: 0.0.0.0:8080

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Content-Length: 0
        Content-Type: application/octet-stream
        Server: Python/3.6 aiohttp/3.2.1

    :query logger: target logger
    :query level: desired level
    :resheader Content-Type: application/json
    :status 204: logger level updated
    :status 400: malformed request
    :status 404: logger and/or level not found
    :status 500: logger could not be updated to desired level
