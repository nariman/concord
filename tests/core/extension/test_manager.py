"""
The MIT License (MIT)

Copyright (c) 2017-2018 Nariman Safiulin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from typing import Sequence

import pytest

from hugo.core.exceptions import ExtensionManagerError
from hugo.core.extension import Extension, Manager
from hugo.core.middleware import (
    AllOfAll,
    Middleware,
    MiddlewareChain,
    MiddlewareState,
    as_middleware,
)


@pytest.fixture(scope="function")
def extension():
    class FirstState:
        pass

    class SecondState:
        pass

    @as_middleware
    async def first_mw(*args, ctx, next, **kwargs):
        pass

    @as_middleware
    async def second_mw(*args, ctx, next, **kwargs):
        pass

    class SomeExtension(Extension):
        on_register_called = False
        on_unregister_called = False

        def __init__(self):
            self._client_middleware = [MiddlewareState(FirstState), first_mw]
            self._extension_middleware = [
                MiddlewareState(SecondState),
                second_mw,
            ]

        @property
        def client_middleware(self) -> Sequence[Middleware]:
            return self._client_middleware

        @property
        def extension_middleware(self) -> Sequence[Middleware]:
            return self._extension_middleware

        def on_register(self, manager: "Manager"):
            assert isinstance(manager, Manager)
            SomeExtension.on_register_called = True

        def on_unregister(self, manager: "Manager"):
            assert isinstance(manager, Manager)
            SomeExtension.on_unregister_called = True

    return SomeExtension


def test_types(extension):
    manager = Manager()

    assert isinstance(manager.client_middleware, Sequence)
    assert isinstance(manager.extension_middleware, Sequence)

    # We have at least one AllOfAll middleware
    assert isinstance(manager.root_middleware, MiddlewareChain)
    assert isinstance(manager.root_middleware.collection[0], AllOfAll)


def test_registering(extension):
    manager = Manager()

    assert len(manager.client_middleware) == 0
    assert len(manager.extension_middleware) == 0
    assert len(manager.root_middleware.collection) == 1
    assert len(manager.root_middleware.collection[0].collection) == 0
    assert not manager.is_extension_registered(extension)

    manager.register_extension(extension)

    assert len(manager.client_middleware) > 0
    assert len(manager.extension_middleware) > 0
    assert len(manager.root_middleware.collection) > 1
    assert len(manager.root_middleware.collection[0].collection) > 0
    assert manager.is_extension_registered(extension)
    assert extension.on_register_called and not extension.on_unregister_called


def test_unregistering(extension):
    manager = Manager()

    manager.register_extension(extension)
    manager.unregister_extension(extension)

    assert len(manager.client_middleware) == 0
    assert len(manager.extension_middleware) == 0
    assert len(manager.root_middleware.collection) == 1
    assert len(manager.root_middleware.collection[0].collection) == 0
    assert not manager.is_extension_registered(extension)
    assert extension.on_register_called and extension.on_unregister_called


def test_registering_and_unregistering_constraints(extension):
    manager = Manager()

    with pytest.raises(ValueError):
        manager.register_extension(42)
    with pytest.raises(ValueError):
        manager.unregister_extension(42)

    with pytest.raises(ValueError):
        manager.register_extension(Middleware)
    with pytest.raises(ValueError):
        manager.unregister_extension(Middleware)

    with pytest.raises(ExtensionManagerError):
        manager.unregister_extension(extension)
    manager.register_extension(extension)
    with pytest.raises(ExtensionManagerError):
        manager.register_extension(extension)
