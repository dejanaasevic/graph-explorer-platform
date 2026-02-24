from django.http import HttpResponse
from django.shortcuts import render
from use_cases import PluginService
from api.model import Graph
from importlib.resources import files

def index(request):
    plugin_service = PluginService()
    plugin_service.load_plugins("graph.data_source")
    plugin_service.load_plugins("graph.visualizer")
    graph: Graph = plugin_service.plugins["graph.data_source"][0].load(file_path=files('data')
                                                                       .joinpath('game_studio_data.json'))
    graph_vis = plugin_service.plugins["graph.visualizer"][0].render(graph)
    return render(request,'index.html', {"graph":graph_vis})