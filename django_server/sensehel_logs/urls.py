"""sensehel_logs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from sensehel_logs_service.views import urls as app_urls

schema_view = get_schema_view(
    title="SenseHel Logger Service API",
    description="API for interacting with the SenseHel Logger Service application",
    version="1.0.0", public=True)

swagger_view = TemplateView.as_view(template_name='swagger-ui.html', extra_context={'schema_url': 'openapi-schema'})
urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    path('openapi/', schema_view, name='openapi-schema'),
    path('swagger-ui/', swagger_view, name='swagger-ui'),
    path('api/', include(app_urls))
]