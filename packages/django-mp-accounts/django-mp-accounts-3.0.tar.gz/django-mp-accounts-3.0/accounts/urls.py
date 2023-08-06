
from django.urls import path

from accounts import views


app_name = 'accounts'


urlpatterns = [

    path('', views.profile, name='profile'),

    path('login/', views.LoginView.as_view(), name='login'),

    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('password/change/', views.PasswordChangeView.as_view(),
         name='password-change'),

    path('password/reset/', views.PasswordResetView.as_view(),
         name='password-reset'),

    path('password/reset/<uidb64>/<token>/',
         views.PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),

    path('signup/', views.SignupView.as_view(), name='signup'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('change/', views.ProfileChangeView.as_view(), name='profile-change'),

    path('remove/', views.RemoveProfileView.as_view(), name='profile-remove'),

]
