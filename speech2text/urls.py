
from django.contrib import admin
from django.urls import path
from speech2text import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('', views.select_audio_type, name='select_audio_type'),
    path('create_recording/', views.create_recording, name='create_recording'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('upload_link/', views.upload_link, name='upload_link'),

]
