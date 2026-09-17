from django.urls import path
from . import views

app_name = 'api_v1'

urlpatterns = [
    # Matrix Solvers API endpoints
    path('matrix/determinant/', views.determinant_api_view, name='matrix_determinant'),
]
