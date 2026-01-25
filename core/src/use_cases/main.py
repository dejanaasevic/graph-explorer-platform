from api.model import Graph
from plugin_recognition import PluginService
from importlib.resources import files

def main():
    plugin_service = PluginService()
    plugin_service.load_plugins("graph.data_source")
    plugin_service.load_plugins("graph.visualizer")
    graph: Graph = plugin_service.plugins["graph.data_source"][0].load(file_path=files('data')
                                                                       .joinpath('game_studio_data.json'))
    graph_vis = plugin_service.plugins["graph.visualizer"][0].render(graph)
    print(graph_vis)

if __name__ == "__main__":
    main()