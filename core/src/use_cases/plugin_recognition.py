from importlib.metadata import entry_points
from typing import List

from api.plugins import Plugin

class PluginService(object):

    def __init__(self):
        self.plugins: dict[str,List[Plugin]] = {}

    def load_plugins(self, group: str):
        self.plugins[group] = []
        for ep in entry_points(group=group):
            p = ep.load()
            plugin: Plugin = p()
            self.plugins[group].append(plugin)