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

from typing import (
    List,
    Optional,
    Union
)

from hugo import exceptions


class Command:
    def __init__(self, slug: str, templates: List[str], callback,
                 short_description: Optional[str]=None,
                 long_description: Optional[str]=None, is_active: bool=True):
        if not isinstance(slug, str):
            raise TypeError("Slug must be a string")

        if not asyncio.iscoroutinefunction(callback):
            raise TypeError('Callback must be a coroutine')

        self.slug = slug
        self.templates = templates
        self.compiled = []
        self.callback = callback
        self.short_description = short_description
        self.long_description = long_description
        self.is_active = is_active

        # If callback is a class method, we should provide an instance
        # to the callback
        self.instance = None

        for template in templates:
            self.compiled.append(re.compile(fr"^\s*{template}(\s.*)*$"))

    def __get__(self, instance, owner):
        # TODO: We should provide a more flexible version...
        # What if two bots in one Python proccess will run? Ik.
        if instance is not None:
            self.instance = instance
        return self

    async def invoke(self, ctx, *args, **kwargs):
        """Invokes callback with given parameters."""
        if self.instance is not None:
            await self.callback(self.instance, *args, ctx=ctx, **kwargs)
        else:
            await self.callback(*args, ctx=ctx, **kwargs)


class Group:
    def __init__(self, name: str, short_description: Optional[str]=None,
                 long_description: Optional[str]=None):
        self.name = name
        self.short_description = short_description
        self.long_description = long_description

        self.subgroups = []
        self.commands = {}

        for name, member in inspect.getmembers(self):
            if isinstance(member, Command):
                self.add_command(member)

    def add_subgroup(self, group):
        """Adds a subgroup to the group."""
        if not isinstance(group, Group):
            raise TypeError("Provided group is not a Group instance")
        if group in self.subgroups:
            raise ValueError("Subgroup is added yet")
        self.subgroups.append(group)

    def remove_subgroup(self, group):
        """Removes a subgroup from the group."""
        if not isinstance(group, Group):
            raise TypeError("Provided group is not a Group instance")
        self.subgroups.remove(group)

    def add_command(self, command: Command):
        """Adds a command to the group."""
        if not isinstance(command, Command):
            raise TypeError("Provided command is not a Command instance")
        if command.slug in self.commands:
            raise ValueError("Command is added yet")
        self.commands[command.slug] = command

    def remove_command(self, command: Union[str, Command]):
        """Removes a command from the group."""
        if isinstance(command, Command):
            command = command.slug
        if not isinstance(command, str):
            raise TypeError("Provided command is not a Command instance or "
                            "command slug")
        return self.commands.pop(command, None)

    @property
    def flatten(self):
        """Returns a list of all commands in group and subgroups."""
        for command in self.commands.values():
            yield command
        for subgroup in self.subgroups:
            yield from subgroup.flatten


def group(group: Group):
    """Group decorator for commands."""
    def decorator(command: Command):
        if not isinstance(command, Command):
            raise TypeError("Callback must be transformed to the Command "
                            "instance before this decorator can be used")
        group.add_command(command)
        return command
    return decorator


def command(slug: str, templates: List[str],
            short_description: Optional[str]=None,
            long_description: Optional[str]=None, is_active: bool=True):
    """Command decorator."""
    def decorator(callback):
        return Command(slug=slug,
                       templates=templates,
                       callback=callback,
                       short_description=short_description,
                       long_description=long_description,
                       is_active=is_active)
    return decorator
