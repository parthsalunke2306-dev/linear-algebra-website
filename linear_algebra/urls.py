from django.urls import path
from . import views

app_name = 'linear_algebra'

urlpatterns = [
    # Public Explorer Dashboard
    path('', views.index_view, name='index'),
    
    # Supabase Authentication Routes
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_confirm_view, name='reset_password'),
    path('profile/', views.profile_view, name='profile'),
    
    # Protected Math Solvers & Visualizers (Secured by Supabase RLS / Auth Decorator)
    path('gaussian/', views.gaussian_view, name='gaussian'),
    path('gf2/', views.gf2_view, name='gf2'),
    path('vectors/', views.vectors_view, name='vectors'),
    path('gram-schmidt/', views.gram_schmidt_view, name='gram_schmidt'),
    path('cofactor/', views.cofactor_view, name='cofactor'),
    path('diagonalization/', views.diagonalization_view, name='diagonalization'),

    # Universal PDF Export Route
    path('export-pdf/<str:solver_type>/', views.export_pdf_view, name='export_pdf'),
]

