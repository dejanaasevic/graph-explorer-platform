import json
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
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
        "workspace_count": range(len(apps.get_app_config('app').workspaces)),
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
    if request.method == 'POST':
        graph_vis = workspace.load_and_render(request.POST.dict())
    else:
        graph_vis = workspace.visualizer.render(workspace.graph)
    return render(request,'index.html', {
        "data_source_plugins": apps.get_app_config('app').data_source_plugins,
        "visualizer_plugins": apps.get_app_config('app').visualizer_plugins,
        "fields":workspace.data_source.fields(),
        "graph":graph_vis,
        "queries": workspace.queries,
        "workspace_id":workspace_id,
        "workspace_count":range(len(apps.get_app_config('app').workspaces)),
    })

def create_workspace(request):
    apps.get_app_config('app').workspaces.append(Workspace())
    response = {"workspace_count":len(apps.get_app_config('app').workspaces)}
    return JsonResponse(response)

def switch_workspace(request, workspace_id):
    workspace: Workspace = apps.get_app_config('app').workspaces[workspace_id]
    if workspace.base_graph is None:
        return redirect('/' + str(workspace_id))
    else:
        return redirect('/' + str(workspace_id) + '/render')

def cli(request, workspace_id):
    workspace: Workspace = apps.get_app_config('app').workspaces[workspace_id]
    if workspace.base_graph is None:
        return HttpResponseBadRequest("Please load the graph object before using the CLI!")
    try:
        message = workspace.cli_input(request.GET.get('command'))
        return HttpResponse(message)
    except Exception as e:
        return HttpResponseBadRequest(str(e))


@csrf_exempt
def apply_queries(request, workspace_id):
    workspace: Workspace = apps.get_app_config('app').workspaces[workspace_id]
    body = json.loads(request.body)
    queries = body.get('queries', [])
    if queries:
        workspace.apply_queries(queries)
    else:
        workspace.clear_queries()
    return JsonResponse({"ok": True})



