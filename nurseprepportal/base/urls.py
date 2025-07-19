from django.urls import path
from . import views
from .views import save_scores

urlpatterns = [
     path('',views.dashboard,name="dashboard"),
     path('save-scores/', save_scores, name='save_scores'), 
]