from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('friends/monthly', views.FriendsLeaderboardMonthly, name = 'friends_monthly'),
    path('friends/all-time', views.FriendsLeaderboardAlltime, name = 'friends_alltime'),
    path('global/monthly', views.GlobalLeaderboardMonthly, name = 'global_monthly'),
    path('global/all-time', views.GlobalLeaderboardAlltime, name = 'global_alltime'),
]