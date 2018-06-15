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

import discord
import pendulum

import hugo
from hugo.command import (
    Template,
    Group,
    command,
    group
)
from hugo import exceptions


class Status(Group):
    def __init__(self):
        super().__init__("Status", "Technical information about the bot")

    @command(slug="status",
             templates=[
                 Template(r"status", allow_short_mention=True),
             ],
             short_description="Bot status",
             long_description="",
             private_messages=True,
             server_messages=True)
    async def status(self, ctx):
        embed = discord.Embed()
        embed.title = ctx.bot.name + " bot"
        embed.description = f"Python bot library v.{hugo.__version__}"
        embed.description += "\n"
        embed.description += f"Discord.py library v.{discord.__version__}"

        total_servers = 0
        total_members = 0
        total_online_members = 0
        total_text_channels = 0
        total_voice_channels = 0

        for server in ctx.bot.servers:
            total_servers += 1

            for member in server.members:
                total_members += 1
                if member.status is discord.Status.online:
                    total_online_members += 1

            for channel in server.channels:
                if channel.type is discord.ChannelType.text:
                    total_text_channels += 1
                elif channel.type is discord.ChannelType.voice:
                    total_voice_channels += 1

        embed.add_field(name="Servers", value=f"{total_servers} total")
        embed.add_field(name="Members", value=f"{total_members} total\n{total_online_members} online")
        embed.add_field(name="Channels", value=f"{total_text_channels + total_voice_channels} total\n{total_text_channels} text\n{total_voice_channels} voice")

        uptime = (pendulum.utcnow() - ctx.bot.uptime).in_words()
        embed.set_footer(text=f"Uptime for {uptime}")

        await ctx.send_message(embed=embed)
