from abc import ABC, abstractmethod
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

class VisualizerPlugin(Plugin):
    @abstractmethod
    def render(self, graph:Graph, **kwargs) -> str:
        pass