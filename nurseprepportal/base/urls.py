from django.urls import path
from . import views
from .views import save_scores

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
     path('',views.dashboard,name="dashboard"),
     path('save-scores/', views.save_scores, name='save_scores'), 
     path('viva-scores/', views.viva_scoring_view, name='viva_scores'), 
     path('final-grades/', views.final_grade_report, name='final_grade_report'),
    path('recalculate/', views.recalculate_grades, name='recalculate_grades'),
    path('download-pdf/', views.download_grade_report_pdf, name='download_grade_report_pdf'),
    path('index/', views.index, name="index"),
    path('ajax/get_activities/', views.get_activities_ajax, name='get_activities_ajax'),


  ]