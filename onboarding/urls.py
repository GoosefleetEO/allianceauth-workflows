"""App URLs"""

# Django
from django.urls import path

# AA Example App
from onboarding import views

app_name: str = "onboarding"

urlpatterns = [
    path("", views.index, name="index"),
]
