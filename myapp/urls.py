from django.urls import path
from . import views
from .views import upload_file

urlpatterns = [
    path('api/home/', views.home_data),

    path('api/file/new/', views.file_new),
    path('api/file/open/', views.file_open),
    path('api/file/save/', views.file_save),
    
    path('api/edit/undo/', views.edit_undo),
    path('api/edit/redo/', views.edit_redo),
    
    path("api/view/toggle_sidebar/", views.toggle_sidebar, name="toggle_sidebar"),

    path('api/file/upload/', upload_file, name="file-upload"),

    path('api/files/', views.list_files, name="file-list"),

    path("api/uml/<str:filename>/", views.get_uml_file),

    path('api/files/<path:filename>/', views.file_detail, name='file-detail'),

    path('api/delete-file/', views.delete_file, name='delete_file'),

    path("api/run-json-to-uml/", views.run_json_to_uml, name="run_json_to_uml"),
]
