from api.model import *
from api.plugins import DataSourcePlugin


class XmlDataSource(DataSourcePlugin):

    def name(self) -> str:
        return "XML Data Source"

    def identifier(self) -> str:
        return "xml_data_source"

    def load(self, **kwargs) -> Graph:
        file_path: str = kwargs.get("file_path")
        if file_path is None:
            raise AttributeError("file_path is required")

        directed: bool = kwargs.get("directed", True)

        graph = Graph(directed=directed)

        return graph