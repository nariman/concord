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

import discord

from hugo.command import (
    Command,
    Group
)


class Bot(discord.Client, Group):
    def __init__(self, name, *, loop=None, **options):
        discord.Client.__init__(self, loop=loop, **options)
        Group.__init__(self, name)

        self.name = name

        self.add_group = self.add_subgroup
        self.remove_group = self.remove_subgroup

    def bot_mentions(self, message: discord.Message=None):
        """Returns all allowed bot mentions."""
        me = (self.user if message is None or message.server is None
              else message.server.me)
        return [
            f"{self.name} ", f"{self.name},",
            f"{me.mention} ", f"{me.mention},",
        ]

    def is_bot_mentioned(self, message: discord.Message):
        for mention in self.bot_mentions(message):
            if message.content.startswith(mention):
                return True

        return False

    def remove_bot_mention(self, content: str):
        for mention in self.bot_mentions():
            if content.startswith(mention):
                return content[len(mention):]
        return content

    @staticmethod
    def is_authored_by_bot(message: discord.Message):
        return message.author.bot

    async def on_message(self, message: discord.Message):
        if (not self.is_bot_mentioned(message) or
                self.is_authored_by_bot(message)):
            return

        content = self.remove_bot_mention(message.content)

        for command in self.flatten:
            for template, compiled in zip(command.templates, command.compiled):
                match = compiled.match(content)

                if match:
                    ctx = Context(self, message, template, match)
                    await ctx.invoke(command, **match.groupdict())
                    return


class Context:
    def __init__(self, bot: Bot, message, template: str, match):
        self.bot = bot
        self.message = message
        self.template = template
        self.match = match

    async def invoke(self, command: Command, *args, **kwargs):
        """Invokes callback with given parameters."""
        await command.invoke(self, *args, **kwargs)
