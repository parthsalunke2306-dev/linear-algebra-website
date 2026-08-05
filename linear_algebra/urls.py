from django.urls import path
from . import views

app_name = 'linear_algebra'

urlpatterns = [
    # Public Routes
    path('', views.public_index_view, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_confirm_view, name='reset_password_confirm'),

    # Protected Routes (@login_required)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('gaussian/', views.gaussian_view, name='gaussian'),
    path('gf2/', views.gf2_view, name='gf2'),
    path('vectors/', views.vectors_view, name='vectors'),
    path('gram-schmidt/', views.gram_schmidt_view, name='gram_schmidt'),
    path('cofactor/', views.cofactor_view, name='cofactor'),
    path('diagonalization/', views.diagonalization_view, name='diagonalization'),
]
