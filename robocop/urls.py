from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('index', views.index, name='index'),
    path('upload_file', views.upload_file, name='upload_file'),
    path('findmatch/<int:file_id>', views.find_match, name='find_match'),
]