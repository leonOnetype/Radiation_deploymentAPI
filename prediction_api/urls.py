from django.urls import path
from .views import RadiationView

urlpatterns = [
    path('predict/', RadiationView.as_view(), name='predict')
]
