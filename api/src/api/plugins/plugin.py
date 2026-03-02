from abc import ABC, abstractmethod
from typing import Dict

from ..model.graph import Graph

class Plugin(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def identifier(self) -> str:
        pass

class DataSourcePlugin(Plugin):
    @abstractmethod
    def load(self, **kwargs) -> Graph:
        pass

    @abstractmethod
    def fields(self) -> Dict[str, str]:
        pass

class VisualizerPlugin(Plugin):
    """
    Base class for visualizer plugins.

    The platform renders the graph inside a fixed DOM structure defined in index.html:

        <svg id="main-svg">
            <g id="graph"></g>
        </svg>

    The render() method must return a <script> block that draws into this structure.
    Zoom and pan are handled by views on #main-svg — the visualizer does not need
    to implement them.

    Required conventions for full platform integration:
    - Render all nodes and edges into d3.select("#graph")
    - Each node element must have class "node" (used by views)
    - #main-svg is available for SVG <defs> (e.g. arrow markers)
    """

    @abstractmethod
    def render(self, graph: Graph, **kwargs) -> str:
        """
        Render the graph as a JavaScript string.

        Returns an HTML <script> block that, when executed in the browser,
        draws the graph into #graph using D3 (v3). The returned string is
        injected directly into the page via Django's {{ graph | safe }} tag.

        Example minimal structure:
            return "<script>d3.select('#graph').append(...)</script>"
        """
        pass