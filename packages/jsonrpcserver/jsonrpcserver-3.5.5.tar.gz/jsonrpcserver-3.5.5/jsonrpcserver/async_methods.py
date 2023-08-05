"""
Asynchronous methods.

Asynchronous version of the :mod:`Methods <jsonrpcserver.methods>` class. Holds
the list of functions that can be called by RPC calls.

Python 3.5+ users can dispatch requests to coroutines. Usage is the same as
synchronous methods, but this time import from ``jsonrpcserver.aio``::

    from jsonrpcserver.aio import methods

    @methods.add
    async def ping():
        return await some_long_running_task()

Then ``await`` the dispatch::

    response = await methods.dispatch(request)
"""
from .async_dispatcher import dispatch
from .methods import Methods


class AsyncMethods(Methods):
    async def dispatch(self, *args, **kwargs):
        return await dispatch(self, *args, **kwargs)

    def serve_forever(self):
        raise NotImplementedError()
