from django.urls import path

from . import views

app_name = 'zhiyuan'
urlpatterns = [
    path('time', views.time, name='time'),
    path('feedback', views.feedback, name='feedback'),
    path('department', views.department, name='department'),
    # path('form', views.user_import, name='form'),
]
