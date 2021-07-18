from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index,  name="Home"),
    path('uploads/', views.uploads,  name="Upload"),
    path('dec/', views.dec,  name="Dec"),
]
