# TG-UserBot - A modular Telegram UserBot script for Python.
# Copyright (C) 2019  Kandarp <https://github.com/kandnub>
#
# TG-UserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TG-UserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TG-UserBot.  If not, see <https://www.gnu.org/licenses/>.


import aiohttp

from userbot import client

plugin_category = "memes"


@client.onMessage(
    command=("shibe", plugin_category),
    outgoing=True, regex="shibe$"
)
async def shibes(event):
    """Get random pictures of Shibes."""
    shibe = await _request('http://shibe.online/api/shibes')
    if not shibe:
        await event.answer("`Couldn't fetch a shibe for you :(`")
        return

    _, json = shibe
    await event.respond(file=json[0], reply_to=event.reply_to_msg_id or None)
    await event.delete()


@client.onMessage(
    command=("cat", plugin_category),
    outgoing=True, regex="cat$"
)
async def cats(event):
    """Get random pictures of Cats."""
    shibe = await _request('http://shibe.online/api/cats')
    if not shibe:
        await event.answer("`Couldn't fetch a cat for you :(`")
        return

    _, json = shibe
    await event.respond(file=json[0], reply_to=event.reply_to_msg_id or None)
    await event.delete()


@client.onMessage(
    command=("bird", plugin_category),
    outgoing=True, regex="bird$"
)
async def birds(event):
    """Get random pictures of Birds."""
    shibe = await _request('http://shibe.online/api/birds')
    if not shibe:
        await event.answer("`Couldn't fetch a bird for you :(`")
        return

    _, json = shibe
    await event.respond(file=json[0], reply_to=event.reply_to_msg_id or None)
    await event.delete()


async def _request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text(), await response.json()
            return None
