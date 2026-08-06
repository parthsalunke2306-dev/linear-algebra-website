from django.urls import path
from . import views

app_name = 'linear_algebra'

urlpatterns = [
    # Public Open Access Solver Tools
    path('', views.public_index_view, name='index'),
    path('gaussian/', views.gaussian_view, name='gaussian'),
    path('gf2/', views.gf2_view, name='gf2'),
    path('vectors/', views.vectors_view, name='vectors'),
    path('gram-schmidt/', views.gram_schmidt_view, name='gram_schmidt'),
    path('cofactor/', views.cofactor_view, name='cofactor'),
    path('diagonalization/', views.diagonalization_view, name='diagonalization'),
]
