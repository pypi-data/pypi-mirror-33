Configuration
=============


Example Configuration
---------------------

An example of the plugin configuration in the ``gordon.toml`` file:

.. literalinclude:: ../gordon.toml.example
    :language: ini


You may choose to have a ``gordon-user.toml`` file for development. Any top-level key will override what's found in ``gordon.toml``.

.. code-block:: ini

    [core]
    debug = true
    plugins = ["introspection"]

    [core.logging]
    level = "debug"
    handlers = ["stream"]

    [introspection]
    host = "0.0.0.0"


Supported Configuration
-----------------------

The following sections are supported:

introspection
~~~~~~~~~~~~~

.. option:: host=STRING

    Host to listen on, ``0.0.0.0`` if not set (default).

.. option:: port=INT

    Port to listen on, ``8080`` if not set (default).
