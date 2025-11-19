from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('solicitar/', views.solicitar_produto, name='solicitar_produto'),
    path('estoque/<int:produto_id>/', views.atualizar_estoque, name='atualizar_estoque'),
    path('produto/novo/', views.cadastrar_produto, name='cadastrar_produto'),
    path('produto/editar/<int:produto_id>/', views.editar_produto, name='editar_produto'),
]
