from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_files'),
    path('login/', views.google_login, name='google_login'),
]
