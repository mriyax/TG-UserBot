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


import dataclasses
import importlib
import inspect
import logging
import os.path
import pathlib
import types
from typing import List, Tuple, Union

from telethon import events, TelegramClient


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Callback:
    name: str
    callback: callable


@dataclasses.dataclass
class Plugin:
    name: str
    callbacks: List[Callback]
    path: str
    module: types.ModuleType


class PluginManager:
    active_plugins: List[Plugin] = []
    inactive_plugins: List[Plugin] = []

    def __init__(self, client: TelegramClient):
        self.client = client
        if "plugins" not in client.config:
            client.config["plugins"] = {}
        config = client.config["plugins"]
        self.plugin_path: str = os.path.relpath(
            config.setdefault("root", "./userbot/plugins")
        )
        self.include: list = self._split_plugins(config.get("include", []))
        self.exclude: list = self._split_plugins(config.get("exclude", []))

    def import_all(self) -> None:
        importlib.invalidate_caches()
        for plugin_name, path in self._list_plugins():
            if self.include and not self.exclude:
                if plugin_name in self.include:
                    self._import_module(plugin_name, path)
                else:
                    self.inactive_plugins.append(
                        Plugin(plugin_name, [], path, None)
                    )
            elif not self.include and self.exclude:
                if plugin_name in self.exclude:
                    self.inactive_plugins.append(
                        Plugin(plugin_name, [], path, None)
                    )
                    LOGGER.debug("Skipped importing %s", plugin_name)
                else:
                    self._import_module(plugin_name, path)
            else:
                self._import_module(plugin_name, path)

    def add_handlers(self) -> None:
        for plugin in self.active_plugins:
            for callback in plugin.callbacks:
                self.client.add_event_handler(callback.callback)
                LOGGER.debug(
                    "Added event handler for %s.", callback.callback.__name__
                )

    def remove_handlers(self) -> None:
        for plugin in self.active_plugins:
            for callback in plugin.callbacks:
                self.client.remove_event_handler(callback.callback)
                LOGGER.debug(
                    "Removed event handlers for %s.",
                    callback.callback.__name__
                )

    def _list_plugins(self) -> List[Union[Tuple[str, str], None]]:
        plugins: List[Tuple[str, str]] = []
        if self.client.config["plugins"].getboolean("enabled", True):
            for f in pathlib.Path(self.plugin_path).glob("**/*.py"):
                if f.name != "__init__.py" and not f.name.startswith('_'):
                    name = f.name[:-3]
                    path = os.path.relpath(f)[:-3]
                    path = path.replace('\\', '.').replace('/', '.')
                    plugins.append((name, path))
        return plugins

    def _import_module(self, name: str, path: str) -> None:
        for plugin in self.active_plugins:
            if plugin.name == name:
                LOGGER.error(
                    "Rename the plugin %s in %s or %s and try again.",
                    name, path, plugin.path
                )
                exit(1)
        try:
            spec = importlib.util.find_spec(path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # To make plugins impoartable use "sys.modules[path] = module".
            callbacks: List[Callback] = []
            for n, cb in vars(module).items():
                if inspect.iscoroutinefunction(cb) and not n.startswith('_'):
                    if events._get_handlers(cb):
                        callbacks.append(Callback(n, cb))
            self.active_plugins.append(Plugin(name, callbacks, path, module))
            LOGGER.info("Successfully Imported %s", name)
        except Exception as E:
            self.client.failed_imports.append(path)
            LOGGER.error(
                "Failed to import %s due to the error(s) below.", path
            )
            LOGGER.exception(E)

    def _split_plugins(self, to_split: str or list) -> None:
        if isinstance(to_split, str):
            if ',' in to_split:
                sep = ','
            else:
                sep = "\n"
            return to_split.split(sep)
        else:
            return to_split
