from django.urls import path, include

from login import views

urlpatterns = [
    path('', views.index, name="index"),  #
    path('login/', views.login, name="login"),  #
    path('admin/login/', views.admin_login, name="admin_login"),  # 添加管理员登录路由
    path('admin/dashboard/', views.admin_dashboard, name="admin_dashboard"),  # 添加管理员仪表板路由
    path('register/', views.reginter, name="register"),  #
    path('pswd_update/', views.pswd_update, name="pswd_update"),  #
    path('logout/', views.logout, name="logout"),  #
    path('api/login/', views.api_login, name='api_login'),  # 添加 API 登录路由
    path('api/admin/login/', views.api_admin_login, name='api_admin_login'),  # 添加管理员 API 登录路由
    path('api/user/info/', views.user_info, name='user_info'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/password/reset/request/', views.api_password_reset_request, name='api_password_reset_request'),
    path('api/password/reset/with_code/', views.api_password_reset_with_code, name='api_password_reset_with_code'),
    
    # ==================== 用户管理模块路由 ====================
    # 用户个人中心
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/evaluations/', views.user_evaluations, name='user_evaluations'),
    path('user/complaints/', views.user_complaints, name='user_complaints'),
    path('user/complaints/<int:complaint_id>/feedback/', views.complaint_feedback, name='complaint_feedback'),
    
    # 管理员用户管理
    path('admin/user/management/', views.admin_user_management, name='admin_user_management'),
    path('admin/complaint/management/', views.admin_complaint_management, name='admin_complaint_management'),
    path('admin/complaint/<int:complaint_id>/', views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin/blacklist/management/', views.admin_blacklist_management, name='admin_blacklist_management'),
    
    # 新增管理员功能模块
    path('admin/evaluation/management/', views.admin_evaluation_management, name='admin_evaluation_management'),
    path('admin/complaint/feedback/', views.admin_complaint_feedback, name='admin_complaint_feedback'),
    path('admin/blacklist/removal/requests/', views.admin_blacklist_removal_requests, name='admin_blacklist_removal_requests'),
    
    # 数据分析模块
    path('admin/data/analysis/', views.admin_data_analysis, name='admin_data_analysis'),
    path('admin/data_analysis/api/', views.admin_data_analysis_api, name='admin_data_analysis_api'),
]
