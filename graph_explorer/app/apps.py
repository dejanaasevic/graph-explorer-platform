from typing import List

from django.apps import AppConfig
from api.plugins import Plugin
from use_cases import PluginService
from use_cases import Workspace

datasource_group = 'graph.data_source'
visualizer_group = 'graph.visualizer'

class PluginAdapter(object):
    def __init__(self, plugin: Plugin):
        self.name = plugin.name()
        self.identifier = plugin.identifier()

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    plugin_service = PluginService()
    data_source_plugins = []
    visualizer_plugins = []
    workspaces: List[Workspace] = [Workspace()]

    def ready(self):
        self.plugin_service.load_plugins(datasource_group)
        self.plugin_service.load_plugins(visualizer_group)
        self.data_source_plugins = [PluginAdapter(plugin) for plugin in self.plugin_service.plugins["graph.data_source"]]
        self.visualizer_plugins = [PluginAdapter(plugin) for plugin in self.plugin_service.plugins["graph.visualizer"]]