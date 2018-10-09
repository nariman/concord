# Concord

Middleware-based event processing library for Discord. Uses
[discord.py](https://github.com/Rapptz/discord.py) under the hood.

[![Build Status](https://img.shields.io/travis/Roolat/concord/dev.svg?style=flat-square)](https://travis-ci.org/Roolat/concord)
[![Codecov](https://img.shields.io/codecov/c/github/Roolat/concord/dev.svg?style=flat-square)](https://codecov.io/gh/Roolat/concord)
[![LGTM total alerts](https://img.shields.io/lgtm/alerts/g/Roolat/concord.svg?style=flat-square)](https://lgtm.com/projects/g/Roolat/concord/alerts/)
[![LGTM language grade: Python](https://img.shields.io/lgtm/grade/python/g/Roolat/concord.svg?style=flat-square)](https://lgtm.com/projects/g/Roolat/concord/context:python)
![License](https://img.shields.io/github/license/Roolat/concord.svg?style=flat-square)

Concord **is not** a library for accessing Discord API. If you're here for an
API library, see [discord.py](https://github.com/Rapptz/discord.py) or
[disco](https://github.com/b1naryth1ef/disco), or
[Discord Developer Documentation](https://discordapp.com/developers/docs/topics/community-resources)
page with a list of libraries for different languages.

## Purpose

The library aims to provide a more convenience way to handle Discord gateway
events, with code reusing where it's possible, including separating
functionality into extensions.  
Event processing is done using the programmer-defined handlers tree. Like in web
applications, due to similarity of the concepts of processing requests, Concord
calls these handlers as middleware as well.

Concord doesn't try to be either a *fast* or a *slow* library. For it's
customization ability, it had to pay the speed.

## Example

[Hugo](https://github.com/Roolat/Hugo) - example bot, built on the Concord. Take
a note, that there's no so much code. It just registers extensions -
third-party middleware sets.  
Actually, Concord - is a successor of Hugo. You can figure this out by code
history.

Example extensions:
[concord-ext-audio](https://github.com/Roolat/concord-ext-audio),
[concord-ext-stats](https://github.com/Roolat/concord-ext-stats).

## Installation

You can install the latest version from PyPi:

```bash
pip install cncrd  # no vowels!
```

Take a note, that `cncrd` has no vowels. PyPi is the only place, where Concord
is named as `cncrd`.  
Also, by now, Concord has a specific requirement - `rewrite` branch of
[discord.py](https://github.com/Rapptz/discord.py). Take care of installing
it too.

```bash
pip install -U https://github.com/Rapptz/discord.py/archive/rewrite.zip#egg=discord.py
```

Concord uses [Poetry](https://github.com/sdispater/poetry) for it's dependency
management. You can add Concord to your project using Poetry:

```bash
poetry add cncrd
```

Poetry will handle the `discord.py` specific version for you.

Concord's development version is located in the `dev` branch, and, in most
cases, it's a pretty stable to use in case you're a bot developer.

## Documentation

I'm really sorry, but there's no online documentation yet.  
But. Concord is a small library, the code is well documented, and, with a
mentioned examples, you can quickly understand everything. Feel free to open an
issue on GitHub, if you need some help.

## License

MIT.  
See LICENSE file for more information.
