from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('', views.cadastro_view, name="cadastro"),
    path('login/', views.login_view, name="login"),
    path('', views.logout_view, name="logout")
]