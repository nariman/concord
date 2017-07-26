"""
Hugo - Discord Bot

MIT License

Copyright (c) 2017 woofilee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import inspect
import re
from functools import partial
from typing import (
    List,
    Optional,
    Union
)

from hugo import exceptions


class Command:
    def __init__(self, slug: str, callback, slashes: List[str],
                 templates: Optional[List[str]]=None,
                 short_description: Optional[str]=None,
                 long_description: Optional[str]=None,
                 private_messages: bool=True,
                 server_messages: bool=True):
        if not isinstance(slug, str):
            raise TypeError("Slug must be a string")

        if not asyncio.iscoroutinefunction(callback):
            raise TypeError("Callback must be a coroutine")

        self.slug = slug
        self.callback = callback
        self.slashes = slashes
        self.templates = templates if templates is not None else []
        self.compiled_slashes = []
        self.compiled_templates = []
        self.short_description = short_description
        self.long_description = long_description
        self.private_messages = private_messages
        self.server_messages = server_messages

        self._compile()

    def add_slash(self, slash):
        """Adds a new slash to the command."""
        self.slashes.append(slash)
        self.compiled_slashes.append(self.compile_slash(slash))

    def add_template(self, template):
        """Adds a new template to the command."""
        self.templates.append(template)
        self.compiled_templates.append(self.compile_template(template))

    def remove_slash(self, slash):
        """Removes the slash from the command."""
        self.slashes.remove(slash)
        self.recompile()

    def remove_template(self, template):
        """Removes the template from the command."""
        self.templates.remove(template)
        self.recompile()

    @staticmethod
    def compile_slash(slash):
        return re.compile(fr"^\s*{slash}(\s.*)*$")

    @staticmethod
    def compile_template(template):
        return re.compile(fr"^\s*{template}(\s.*)*$")

    def _compile_slashes(self):
        for slash in self.slashes:
            self.compiled_slashes.append(self.compile_slash(slash))

    def _compile_templates(self):
        for template in self.templates:
            self.compiled_templates.append(self.compile_template(template))

    def _compile(self):
        self._compile_slashes()
        self._compile_templates()

    def recompile(self):
        self.compiled_slashes = []
        self.compiled_templates = []
        self._compile()

    async def __call__(self, *args, **kwargs):
        """Invokes callback with given parameters."""
        return await self.invoke(*args, **kwargs)

    async def invoke(self, *args, **kwargs):
        """Invokes callback with given parameters."""
        return await self.callback(*args, **kwargs)


class Group:
    def __init__(self, name: str, short_description: Optional[str]=None,
                 long_description: Optional[str]=None):
        self.name = name
        self.short_description = short_description
        self.long_description = long_description

        self.subgroups = []
        self.commands = []

        for name, member in inspect.getmembers(self):
            if is_command(member):
                self.add_command(member)

    def add_subgroup(self, group):
        """Adds a subgroup to the group."""
        if not isinstance(group, Group):
            raise TypeError("Provided group is not a Group instance")
        if group in self.subgroups:
            raise ValueError("Subgroup is added yet")
        self.subgroups.append(group)

    def remove_subgroup(self, group):
        """Removes the subgroup from the group."""
        self.subgroups.remove(group)

    def add_command(self, callback):
        """Adds a command to the group."""
        if not is_command(callback):
            raise TypeError("Provided callback is not a command")
        if callback in self.commands:
            raise ValueError("Command is added yet")
        self.commands.append(callback)

    def remove_command(self, callback):
        """Removes the command from the group."""
        self.commands.remove(callback)

    @property
    def flatten(self):
        """Returns a list of all commands in group and subgroups."""
        for command in self.commands:
            yield command
        for subgroup in self.subgroups:
            yield from subgroup.flatten


def is_command(callback):
    """Checks is given callback a Command."""
    if not isinstance(getattr(callback, "command", None), Command):
        return False
    return True


def group(group: Group):
    """Group decorator for commands."""
    def decorator(callback):
        if not is_command(callback):
            raise TypeError("Callback must be transformed to the command "
                            "before this decorator can be used")
        group.add_command(callback)
        return callback
    return decorator


def command(slug: str, slashes: List[str], templates: Optional[List[str]]=None,
            short_description: Optional[str]=None,
            long_description: Optional[str]=None,
            private_messages: bool=True, server_messages: bool=True):
    """Command decorator."""
    def decorator(callback):
        command = Command(slug=slug,
                          callback=callback,
                          slashes=slashes,
                          templates=templates,
                          short_description=short_description,
                          long_description=long_description,
                          private_messages=private_messages,
                          server_messages=server_messages)

        async def wrapper(*args, **kwargs):
            return await command.invoke(*args, **kwargs)

        wrapper.command = command
        return wrapper
    return decorator
