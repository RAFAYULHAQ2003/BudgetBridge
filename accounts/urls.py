from django.urls import path
from .views import landing_view, login_view, dashboard_view, logout_view

urlpatterns = [
    path("", landing_view, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),

]