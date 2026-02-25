from api.model import Graph
from plugin_recognition import PluginService
from importlib.resources import files
from pathlib import Path

def main():
    plugin_service = PluginService()
    plugin_service.load_plugins("graph.data_source")
    plugin_service.load_plugins("graph.visualizer")

    #json

    graph: Graph = plugin_service.plugins["graph.data_source"][0].load(file_path=files('data')
                                                                       .joinpath('game_studio_data.json'))
    graph_vis = plugin_service.plugins["graph.visualizer"][0].render(graph)
    print(graph_vis)

    #xml

    xml_data_path = Path(
        __file__).resolve().parent.parent.parent.parent / "xml_data_source" / "data" / "acyclic_company.xml"

    graph: Graph = plugin_service.plugins["graph.data_source"][1].load(
        file_path=xml_data_path
    )
    graph_vis = plugin_service.plugins["graph.visualizer"][0].render(graph)
    print(graph_vis)


if __name__ == "__main__":
    main()


