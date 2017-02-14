from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView, DetailView

# For serving media files
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from views import *

# Create a router and register our viewsets with it.
router = DefaultRouter()

urlpatterns = patterns(
        '',
        url(r'^', include(router.urls)),
        url(r'^docs/', include('rest_framework_swagger.urls')),
        url(r'^upload_card', upload_card),
        url(r'^verify', upload_portrait_and_verify)
)
