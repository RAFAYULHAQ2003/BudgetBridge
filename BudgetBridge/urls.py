"""
URL configuration for BudgetBridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
# from BudgetBridge import settings
from django.conf import settings 
from django.conf.urls.static import static
from accounts.views import landing_view
from django.conf.urls import handler404, handler500, handler403, handler400


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
    path('', landing_view, name='home'),  
    path("accounts/", include("accounts.urls")), 
    path("workforce/", include("workforce.urls")), 
    path("operations/", include("operations.urls")),
    path("finance/", include("finance.urls")),
   
]


handler404 = "BudgetBridge.views.handler404"
handler500 = "BudgetBridge.views.handler500"
handler403 = "BudgetBridge.views.handler403"
handler400 = "BudgetBridge.views.handler400"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
