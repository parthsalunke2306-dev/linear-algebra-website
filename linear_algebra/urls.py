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
    # Unit 1
    path('gaussian/', views.gaussian_view, name='gaussian'),
    path('gf2/', views.gf2_view, name='gf2'),
    path('vectors/', views.vectors_view, name='vectors'),
    # Unit 2
    path('gram-schmidt/', views.gram_schmidt_view, name='gram_schmidt'),
    path('cofactor/', views.cofactor_view, name='cofactor'),
    path('diagonalization/', views.diagonalization_view, name='diagonalization'),
    # Unit 3
    path('divisibility/', views.divisibility_view, name='divisibility'),
    path('euclidean/', views.euclidean_view, name='euclidean'),
    # Unit 4
    path('complex-polar/', views.complex_polar_view, name='complex_polar'),
    path('demoivre/', views.demoivre_view, name='demoivre'),
    # Unit 5
    path('permutations-combinations/', views.permutations_combinations_view, name='permutations_combinations'),
    # Unit 6
    path('functions/', views.functions_view, name='functions'),
    # Unit 7
    path('limits/', views.limits_view, name='limits'),
    # Interactive Lab
    path('quiz/', views.quiz_view, name='quiz'),
    path('ai-tutor/', views.ai_tutor_view, name='ai_tutor'),

    # Universal PDF Export Route
    path('export-pdf/<str:solver_type>/', views.export_pdf_view, name='export_pdf'),
]

