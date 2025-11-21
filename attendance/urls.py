from django.urls import path
from . import views
from . import reports

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Devotee URLs
    path('devotees/', views.devotee_list, name='devotee_list'),
    path('devotees/add/', views.devotee_add, name='devotee_add'),
    path('devotees/<str:pk>/', views.devotee_detail, name='devotee_detail'),
    path('devotees/edit/<str:pk>/', views.devotee_edit, name='devotee_edit'),
    path('devotees/delete/<str:pk>/', views.devotee_delete, name='devotee_delete'),
    
    # Sabha URLs
    path('sabhas/', views.sabha_list, name='sabha_list'),
    path('sabhas/add/', views.sabha_add, name='sabha_add'),
    path('sabhas/<str:sabha_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    
    # Reports
    path('reports/', reports.reports_dashboard, name='reports_dashboard'),
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/export/', views.export_attendance, name='export_attendance'),
    path('reports/sabha-wise/', reports.sabha_wise_report, name='sabha_wise_report'),
    path('reports/mandal-wise/', reports.mandal_wise_report, name='mandal_wise_report'),
    path('reports/xetra-wise/', reports.xetra_wise_report, name='xetra_wise_report'),
    path('reports/trends/', reports.attendance_trends, name='attendance_trends'),
    path('reports/devotee-history/', reports.devotee_attendance_history, name='devotee_attendance_history'),
    
    # Upload
    path('upload/', views.upload_devotees, name='upload_devotees'),
    
    # AJAX
    path('attendance/save/', views.save_individual_attendance, name='save_individual_attendance'),
    path('api/save-attendance/', views.save_individual_attendance, name='api_save_attendance'),

]