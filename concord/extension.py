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

import logging
from typing import Dict, Sequence, Type, Optional

from concord.exceptions import ExtensionManagerError
from concord.middleware import (
    Middleware,
    MiddlewareChain,
    chain_of,
    sequence_of,
)


log = logging.getLogger(__name__)


class Extension:
    """Abstract extension class.

    TODO: What about dependencies of extension?
          It would be cool, and seems like not hard to implement.
    """

    NAME = "Extension name is empty."
    DESCRIPTION = "Extension description is empty."
    VERSION = "1.0.0"

    @property
    def client_middleware(self) -> Sequence[Middleware]:
        """Middleware list, associated with this extension, and that should be
        registered and applied on every event processing.

        It is especially useful for sharing states between different extensions.

        .. note::
            Keep in mind, that this list can be requested multiple times as well
            as cached and optimized. You should return the same list on every
            request and avoid any changes in the list after first request due to
            this changes may be unexpected for other code.

        .. warning::
            Keep in mind, that client middleware will be executed by middleware
            chain.
        """
        return []

    @property
    def extension_middleware(self) -> Sequence[Middleware]:
        """Middleware list, associated with this extension, and that should be
        registered for event handling.

        .. note::
            Keep in mind, that this list can be requested multiple times as well
            as cached and optimized. You should return the same list on every
            request and avoid any changes in the list after first request due to
            this changes may be unexpected for other code.

        .. warning::
            Keep in mind, that all extension middleware will be executed on
            every event. Properly filter events before processing them.
        """
        return []

    def on_register(self, manager: "Manager"):
        """Listener invoked on registering extension in a manager.

        If there's global states and middleware, associated with this extension,
        all of this will be registered after invoking this listener.

        Args:
            manager: Manager instance where extension has been registered.
        """
        pass  # pragma: no cover

    def on_unregister(self, manager: "Manager"):
        """Listener invoked on unregistering extension in a manager.

        If there's global states and middleware, associated with this extension,
        all of this is already unregistered before invoking this listener.

        Args:
            manager: Manager instance where extension has been unregistered.
        """
        pass  # pragma: no cover


class Manager:
    """Extension manager.

    Attributes:
        _extensions: List of registered extensions. Key is an extension class
            (subclass of :class:`Extension`), value is extension instance.
        _client_middleware_cache: Cached list of client middleware.
        _extension_middleware_cache: Cached list of extension middleware.
        _root_middleware_cache: Cached root middleware.
    """

    _extensions: Dict[Type[Extension], Extension]
    _client_middleware_cache: Optional[Sequence[Middleware]]
    _extension_middleware_cache: Optional[Sequence[Middleware]]
    _root_middleware_cache: Optional[Middleware]

    def __init__(self):
        self._extensions = {}
        self._client_middleware_cache = None
        self._extension_middleware_cache = None
        self._root_middleware_cache = None

    @property
    def client_middleware(self) -> Sequence[Middleware]:
        """States list, provided by extensions, and that should be applied on
        every event processing."""
        if self._client_middleware_cache is None:
            self._client_middleware_cache = [
                mw
                for extension in self._extensions.values()
                for mw in extension.client_middleware
            ]
        return self._client_middleware_cache

    @property
    def extension_middleware(self) -> Sequence[Middleware]:
        """Middleware list, provided by extensions for event handling."""
        if self._extension_middleware_cache is None:
            self._extension_middleware_cache = [
                mw
                for extension in self._extensions.values()
                for mw in extension.extension_middleware
            ]

        return self._extension_middleware_cache

    @property
    def root_middleware(self) -> MiddlewareChain:
        """Root middleware, a built chain of client and extension middleware."""
        if self._root_middleware_cache is None:
            chain = chain_of([sequence_of(self.extension_middleware)])
            for mw in self.client_middleware:
                chain.add_middleware(mw)
            self._root_middleware_cache = chain
        return self._root_middleware_cache

    def is_extension_registered(self, extension: Type[Extension]) -> bool:
        """Checks is extension registered in the manager.

        Args:
            extension: Extension to check.

        Returns:
            ``True``, if extensions is registered, otherwise ``False``.
        """
        return extension in self._extensions

    def register_extension(self, extension: Type[Extension]):
        """Register extension in the manager.

        Args:
            extension: Extension to register.

        Raises:
            ValueError: If not a type provided or if provided type is not a
                subclass of :class:`Extension` provided.
            concord.exceptions.ExtensionManagerError: If this extension is
                already registered in this manager.
        """
        if not isinstance(extension, type):
            raise ValueError("Not a type")
        if not issubclass(extension, Extension):
            raise ValueError("Not an extension")
        if self.is_extension_registered(extension):
            raise ExtensionManagerError("Already registered")

        instance = extension()
        instance.on_register(self)
        self._extensions[extension] = instance
        self._client_middleware_cache = None
        self._extension_middleware_cache = None
        self._root_middleware_cache = None

        log.info(
            f'Extension "{extension.NAME} "'
            f"(version {extension.VERSION}) has been registered"
        )

    def unregister_extension(self, extension: Type[Extension]):
        """Unregister extension in the manager.

        Args:
            extension: Extension to unregister.

        Raises:
            ValueError: If not a type provided or if provided type is not a
                subclass of :class:`Extension` provided.
            concord.exceptions.ExtensionManagerError: If this extension is not
                registered in this manager.
        """
        if not isinstance(extension, type):
            raise ValueError("Not a type")
        if not issubclass(extension, Extension):
            raise ValueError("Not an extension")
        if not self.is_extension_registered(extension):
            raise ExtensionManagerError("Not registered")

        instance = self._extensions.pop(extension)
        self._client_middleware_cache = None
        self._extension_middleware_cache = None
        self._root_middleware_cache = None
        instance.on_unregister(self)

        log.info(
            f'Extension "{extension.NAME} "'
            f"(version {extension.VERSION}) has been unregistered"
        )
