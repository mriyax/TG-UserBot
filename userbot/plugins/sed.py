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


# This is based on https://github.com/SijmenSchoon/regexbot
# but slightly different.
# https://stackoverflow.com/a/46100580 is also very helpful with the
# explanation on how we could make it work and what we'd need to check.


from asyncio import sleep
from re import match, DOTALL, MULTILINE, IGNORECASE

from userbot import client
from userbot.helper_funcs.sed import sub_matches


REGEXNINJA = False

pattern = (
    r'(?:^|;.+?)'  # Ensure that the expression doesn't go blatant
    r'([1-9]+?)?'  # line: Don't match a 0, sed counts lines from 1
    r'(?:sed|s)'  # The s command (as in substitute)
    r'(?:(?P<d>.))'  # Unknown delimiter with a named group d
    r'((?:(?!(?<![^\\]\\)(?P=d)).)+)'  # regexp
    r'(?P=d)'  # Unknown delimiter
    r'((?:(?!(?<![^\\]\\)(?P=d)|(?<![^\\]\\);).)*)'  # replacement
    r'(?:(?=(?P=d)|;).)?'  # Check if it's a delimiter or a semicolon
    r'((?<!;)\w+)?'  # flags: Don't capture if it starts with a semicolon
    r'(?=;|$)'  # Ensure it ends with a semicolon for the next match
)


@client.onMessage(
    command="sed", info="GNU sed like substitution", disable_prefix=True,
    outgoing=True, regex=(pattern, MULTILINE | IGNORECASE | DOTALL)
)
async def sed_substitute(event):
    """SED function used to substitution texts for s command"""
    if not match(r"^(?:[1-9]+sed|[1-9]+s|sed)", event.raw_text, IGNORECASE):
        return

    matches = event.matches
    reply = await event.get_reply_message()

    try:
        if reply:
            original = reply
            if not original:
                return

            newStr = await sub_matches(matches, original.raw_text)
            if newStr:
                await original.reply('[SED]\n\n' + newStr)
        else:
            total_messages = []  # Append messages to avoid timeouts
            count = 0  # Don't fetch more than ten texts/captions

            async for msg in client.iter_messages(
                event.chat_id,
                offset_id=event.message.id
            ):
                if msg.raw_text:
                    total_messages.append(msg)
                    count += 1
                else:
                    continue
                if count >= 10:
                    break

            for message in total_messages:
                newStr = await sub_matches(matches, message.raw_text)
                if newStr:
                    await message.reply('[SED]\n\n' + newStr)
                    break
    except Exception as e:
        await event.reply((
            f"{event.raw_text}"
            '\n\n'
            'Like regexbox says, fuck me.\n'
            '`'
            f"{str(type(e))}"
            ':` `'
            f"{str(e)}"
            '`'
        ))


@client.onMessage(
    command="regexninja", info="Enable or disable regex ninja",
    outgoing=True, regex=r"regexninja(?: |$)(on|off)$"
)
async def regex_ninja(event):
    global REGEXNINJA
    arg = event.matches[0].group(1)

    if not arg:
        if REGEXNINJA:
            await event.edit("`Regex ninja is enabled.`")
        else:
            await event.edit("`Regex ninja is disabled.`")
        return

    if arg == "on":
        REGEXNINJA = True
        value = "enabled"
    else:
        REGEXNINJA = False
        value = "disabled"

    await event.edit(f"`Successfully {value} ninja mode for regexbot!`")
    await sleep(2)
    await event.delete()


@client.onMessage(
    outgoing=True, disable_prefix=True,
    regex=(r'^s/((?:\\/|[^/])+)/((?:\\/|[^/])*)(/.*)?', IGNORECASE)
)
async def ninja(event):
    if REGEXNINJA:
        await sleep(0.5)
        await event.delete()
