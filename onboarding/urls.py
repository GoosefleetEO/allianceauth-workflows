"""App URLs"""

# Django
from django.urls import path

# AA Example App
from onboarding import views

app_name: str = "onboarding"

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:wiz_id>', views.view_wizard_by_id, name='view_wizard_by_id'),
    path('<int:wiz_id>/', views.view_wizard_by_id, name='view_wizard_by_id'),
    path('<int:wiz_id>/<int:step_id>', views.view_wizard_by_id, name='view_wizard_by_id'),
    path('<str:permalink>', views.view_wizard_by_permalink, name='view_wizard'),
    path('<str:permalink>/', views.view_wizard_by_permalink, name='view_wizard'),
    path('<str:permalink>/<int:step_id>', views.view_wizard_by_permalink, name='view_wizard'),
]
