from django.urls import path
from .views import gTranslate

urlpatterns = [
    path('<src>/<dest>/<text>', gTranslate)
]