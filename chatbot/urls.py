from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('descargar-backup/', views.backup_inventario, name='descargar_backup'),
    path('enviar/', views.enviar_paquetes, name='enviar_paquetes'),
]
    
