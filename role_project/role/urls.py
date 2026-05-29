from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/teams/create/', views.create_team, name='create_team'),
    path('admin-dashboard/users/create/', views.create_user, name='create_user'),
    path('admin-dashboard/users/<int:user_id>/assign-team/', views.assign_team, name='assign_team'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('leader-dashboard/', views.leader_dashboard, name='leader_dashboard'),
    path('leader-dashboard/members/create/', views.leader_create_member, name='leader_create_member'),
    path('member-dashboard/', views.member_dashboard, name='member_dashboard'),
]
