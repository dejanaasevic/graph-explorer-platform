from django.http import HttpResponse
from django.shortcuts import render
from django.apps import apps
from use_cases import PluginService
from api.model import Graph
from api.plugins import Plugin
from importlib.resources import files

class PluginBridge(object):
    def __init__(self, plugin: Plugin):
        self.name = plugin.name()
        self.identifier = plugin.identifier()

def index(request):
    plugin_service: PluginService = apps.get_app_config('app').plugin_service
    graph: Graph = plugin_service.plugins["graph.data_source"][0].load(file_path=files('data')
                                                                       .joinpath('game_studio_data.json'))
    graph_vis = plugin_service.plugins["graph.visualizer"][0].render(graph)
    data_source_plugins = [PluginBridge(plugin) for plugin in plugin_service.plugins["graph.data_source"]]
    visualizer_plugins = [PluginBridge(plugin) for plugin in plugin_service.plugins["graph.visualizer"]]
    fields = {}
    if request.GET.get('datasource') != None:
        for plugin in plugin_service.plugins["graph.data_source"]:
            if plugin.identifier() == request.GET.get('datasource'):
                fields = plugin.fields()

    return render(request,'index.html', {
        "graph":graph_vis,
        "data_source_plugins":data_source_plugins,
        "visualizer_plugins":visualizer_plugins,
        "fields":fields
    })

def data_source(request, data_source_id):
    pass