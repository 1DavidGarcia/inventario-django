from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # ← login puro
    path('index/', views.index, name='index'),  # ← dashboard real
    path('auth/', views.auth_view, name='auth_view'),
    path('logout/', views.logout_view, name='logout'),
    path('descargar-backup/', views.backup_inventario, name='descargar_backup'),
    path('enviar/', views.enviar_paquetes, name='enviar_paquetes'),
    path('inventario-crud/', views.inventario_crud, name='inventario_crud'),
    path('api/resumen-inventario/', views.resumen_inventario, name='resumen_inventario'),
    path('sucursales/', views.sucursales_view, name='sucursales'),
]


