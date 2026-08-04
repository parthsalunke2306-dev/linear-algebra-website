from django.urls import path
from . import views

app_name = 'linear_algebra'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('control-center/', views.admin_panel_view, name='admin_panel'),
    path('gaussian/', views.gaussian_view, name='gaussian'),
    path('gf2/', views.gf2_view, name='gf2'),
    path('vectors/', views.vectors_view, name='vectors'),
    path('gram-schmidt/', views.gram_schmidt_view, name='gram_schmidt'),
    path('cofactor/', views.cofactor_view, name='cofactor'),
    path('diagonalization/', views.diagonalization_view, name='diagonalization'),
]
