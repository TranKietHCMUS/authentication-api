from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.UserLogin.as_view(), name='login'),
    path('auth/register/', views.UserRegister.as_view(), name='register'),
    path('auth/logout/', views.UserLogout.as_view(), name='logout'),
    path('user/userview/', views.UserView.as_view(), name='userview'),
    path('token/refresh/', views.RefreshToken.as_view(), name='refresh-token')
]