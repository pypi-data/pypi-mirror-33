from django.urls import path
from .views import gTranslateAuth

urlpatterns = [
    path('<src>/<dest>/<text>', gTranslateAuth)
]