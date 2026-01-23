from api.model import *
from api.plugins import DataSourcePlugin

class JsonDataSource(DataSourcePlugin):
    def name(self) -> str:
        return "Json Data Source"

    def identifier(self) -> str:
        return "json_data_source"

    def load(self, **kwargs) -> Graph:
        pass