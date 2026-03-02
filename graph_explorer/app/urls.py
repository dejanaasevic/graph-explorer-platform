from django.urls import path
from . import views

urlpatterns = [
    path('', views.init, name='init'),
    path('<int:workspace_id>/', views.index, name='index'),
    path('<int:workspace_id>/select_vis', views.select_vis),
    path('<int:workspace_id>/render', views.render_graph, name='render'),
    path('create_workspace', views.create_workspace),
    path('workspace/<int:workspace_id>', views.switch_workspace),
]