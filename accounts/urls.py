from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginUser),
    path('register/', views.registerUser, name='registerUser'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
]
