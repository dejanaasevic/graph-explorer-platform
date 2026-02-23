from django.apps import AppConfig
from use_cases.plugin_recognition import PluginService


datasource_group = 'graph_explorer.datasource'

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    plugin_service = PluginService()

    def ready(self):
        self.plugin_service.load_plugins(datasource_group)