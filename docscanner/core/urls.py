from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path("", views.home, name="home"),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),

    # User URLs
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/scanUpload/', views.perform_scan, name='perform_scan'),
    path('export-scan-history/', views.export_scan_history, name='export_scan_history'),
    path('download-document/<int:doc_id>/', views.download_document, name='download_document'),

    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/review_request/<int:request_id>/', views.review_credit_request, name='review_credit_request'),
]
