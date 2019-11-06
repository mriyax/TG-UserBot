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


import asyncio
import inspect
import sys

from userbot import client
from userbot.utils.helpers import get_chat_link
from userbot.utils.events import NewMessage


plugin_category = "terminal"


@client.onMessage(
    command=("eval", plugin_category),
    outgoing=True, regex=r"eval(?: |$)([\s\S]*)"
)
async def evaluate(event: NewMessage.Event) -> None:
    """Evaluate something in the running script."""
    expression = event.matches[0].group(1).strip()
    reply = await event.get_reply_message()
    if not expression:
        await event.answer("Evaluated the void.")
        return

    try:
        result = eval(
            expression, {'client': client, 'event': event, 'reply': reply}
        )
        if inspect.isawaitable(result):
            result = await result
        result = str(result)
    except Exception as e:
        await event.answer('`' + type(e).__name__ + ': ' + str(e) + '`')
        return

    extra = await get_chat_link(event, event.id)
    await event.answer(
        "```" + result + "```",
        log=("eval", f"Successfully evaluated {expression} in {extra}!"),
        reply=True
    )


@client.onMessage(
    command=("exec", plugin_category),
    outgoing=True, regex=r"exec(?: |$)([\s\S]*)"
)
async def execute(event: NewMessage.Event) -> None:
    """Execute Python code in a subprocess."""
    message = (
        str(event.chat_id) +
        ':' +
        str(event.message.id)
    )
    if client.running_processes.get(message, False):
        await event.answer(
            "A process for this event is already running!",
            reply=True
        )
        return

    code = event.matches[0].group(1).strip()
    if not code:
        await event.answer("Executed the void.")
        return

    process = await asyncio.create_subprocess_exec(
        sys.executable, '-c', code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    client.running_processes.update({
        message: process
    })
    stdout, stderr = await process.communicate()

    not_killed = client.running_processes.get(message, False)
    if not_killed:
        del client.running_processes[message]

    text = f"[EXEC] Return code: {process.returncode}\n"

    if stdout:
        text += "\n[stdout]\n" + stdout.decode("UTF-8").strip() + "\n"
    if stderr:
        text += "\n[stderr]\n" + stderr.decode('UTF-8').strip() + "\n"

    extra = await get_chat_link(event, event.id)
    if stdout or stderr:
        await event.answer(
            "```" + text + "```",
            log=("exec", f"Successfully executed {code} in {extra}!"),
            reply=True
        )
    else:
        await event.answer("Nice, get off the void.\nNo output for you.")


@client.onMessage(
    command=("term", plugin_category),
    outgoing=True, regex=r"term(?: |$)([\s\S]*)"
)
async def terminal(event: NewMessage.Event) -> None:
    """Execute terminal commands in a subprocess."""
    message = (
        str(event.chat_id) +
        ':' +
        str(event.message.id)
    )
    if client.running_processes.get(message, False):
        await event.answer(
            "A process for this event is already running!",
            reply=True
        )
        return

    cmd = event.matches[0].group(1).strip()
    if not cmd:
        await event.answer("Executed the void.")
        return

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    client.running_processes.update({
        message: process
    })
    stdout, stderr = await process.communicate()

    not_killed = client.running_processes.get(message, False)
    if not_killed:
        del client.running_processes[message]

    text = f"[TERM] Return code: {process.returncode}\n"

    if stdout:
        text += "\n[stdout]\n" + stdout.decode("UTF-8").strip() + "\n"
    if stderr:
        text += "\n[stderr]\n" + stderr.decode('UTF-8').strip() + "\n"

    extra = await get_chat_link(event, event.id)
    if stdout or stderr:
        await event.answer(
            "```" + text + "```",
            log=("term", f"Successfully executed {cmd} in {extra}!"),
            reply=True
        )
    else:
        await event.answer("Nice, get off the void.\nNo output for you.")


@client.onMessage(
    command=("kill/terminate", plugin_category),
    outgoing=True, regex=r"(kill|terminate)$",
    info="Kill or Terminate a subprocess which is still running"
)
async def killandterminate(event: NewMessage.Event) -> None:
    """Kill or terminate a running subprocess."""
    if not event.reply_to_msg_id:
        await event.answer(
            "`Reply to a message to kill or terminate the process!`"
        )
        return

    reply = await event.get_reply_message()
    message = (
        str(reply.chat_id) + ':' + str(reply.id)
    )
    running_process = client.running_processes.get(message, False)

    if running_process:
        # If we ever want to wait for it to complete. (Most likely never)
        """try:
            await running_process.wait()
        finally:
            if running_process.returncode is None:"""

        option = event.matches[0].group(1)
        if option == "kill":
            running_process.kill()
        else:
            running_process.terminate()
        extra = await get_chat_link(event, reply.id)
        await event.answer(
            f"`Successfully {option}ed the process.`",
            log=(option, f"Successfully {option}ed a process in {extra}!"),
            reply=True
        )
        await asyncio.sleep(2)
        await event.delete()
    else:
        await event.answer("`There is no process running for this message.`")
