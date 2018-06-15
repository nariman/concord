"""
Hugo - Discord Bot

MIT License

Copyright (c) 2017-2018 Nariman Safiulin

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


class Template:
    def __init__(self, template: str, allow_short_mention=False):
        self.template = template
        self.compiled = re.compile(fr"^\s*{template}(\s.*)*$")
        self.allow_short_mention = allow_short_mention


class Command:
    def __init__(self, slug: str, callback,
                 templates: List[Template],
                 short_description: Optional[str]=None,
                 long_description: Optional[str]=None,
                 private_messages: bool=True, server_messages: bool=True):
        if not isinstance(slug, str):
            raise TypeError("Slug must be a string")

        if not asyncio.iscoroutinefunction(callback):
            raise TypeError("Callback must be a coroutine")

        self.slug = slug
        self.callback = callback
        self.templates = []
        self.short_description = short_description
        self.long_description = long_description
        self.private_messages = private_messages
        self.server_messages = server_messages

        for template in templates:
            self.add_template(template)

    def add_template(self, template: Template):
        """Adds a new template to the command."""
        if not isinstance(template, Template):
            raise TypeError("Template should be Template instance")
        if template in self.templates:
            raise ValueError("Template is added yet")
        self.templates.append(template)

    def remove_template(self, template):
        """Removes the template from the command."""
        self.templates.remove(template)

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


def command(slug: str, templates: List[Template],
            short_description: Optional[str]=None,
            long_description: Optional[str]=None,
            private_messages: bool=True, server_messages: bool=True):
    """Command decorator."""
    def decorator(callback):
        command = Command(slug=slug,
                          callback=callback,
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
