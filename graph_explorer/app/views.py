from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
from use_cases import PluginService, Workspace

def index(request, workspace_id):
    workspace: Workspace = apps.get_app_config('app').workspaces[workspace_id]
    plugin_service: PluginService = apps.get_app_config('app').plugin_service
    fields = {}
    if request.GET.get('datasource') != None:
        for plugin in plugin_service.plugins["graph.data_source"]:
            if plugin.identifier() == request.GET.get('datasource'):
                workspace.set_data_source(plugin)
                fields = plugin.fields()

    return render(request,'index.html', {
        "data_source_plugins":apps.get_app_config('app').data_source_plugins,
        "visualizer_plugins":apps.get_app_config('app').visualizer_plugins,
        "fields":fields,
        "workspace_id":workspace_id,
    })

def init(request):
    return redirect('/0')

def select_vis(request, workspace_id):
    workspace: Workspace = apps.get_app_config('app').workspaces[workspace_id]
    plugin_service: PluginService = apps.get_app_config('app').plugin_service

    if request.GET.get('visualizer') != None:
        for plugin in plugin_service.plugins["graph.visualizer"]:
            if plugin.identifier() == request.GET.get('visualizer'):
                workspace.set_visualizer(plugin)

    return HttpResponse("visualizer selected!")

@csrf_exempt
def render_graph(request, workspace_id):
    workspace: Workspace = apps.get_app_config('app').workspaces[workspace_id]
    graph_vis = workspace.load_and_render(request.POST.dict())
    return render(request,'index.html', {
        "data_source_plugins": apps.get_app_config('app').data_source_plugins,
        "visualizer_plugins": apps.get_app_config('app').visualizer_plugins,
        "fields":workspace.data_source.fields(),
        "graph":graph_vis,
        "workspace_id":workspace_id,
    })

def create_workspace(request):
    pass