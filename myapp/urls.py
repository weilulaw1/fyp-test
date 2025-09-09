from django.urls import path
from . import views
from .views import upload_file

urlpatterns = [
    path('api/home', views.home_data),

    path('api/file/new/', views.file_new),
    path('api/file/open/', views.file_open),
    path('api/file/save/', views.file_save),
    
    path('api/edit/undo/', views.edit_undo),
    path('api/edit/redo/', views.edit_redo),
    
    path("api/view/toggle_sidebar/", views.toggle_sidebar, name="toggle_sidebar"),

    path('api/file/upload', upload_file, name='file-upload'),

]
