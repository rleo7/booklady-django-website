from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.Home, name = 'home'),
    path('about/', views.About, name = 'about'),
    path('contact-page/', views.contact, name = 'contact_page'),
    path('legal-page/', views.LegalPage, name = 'legal_page'),
    path('profile/', views.profile, name = 'profile'),
    path('login/', views.LoginView.as_view(template_name='userLogin.html'), name = 'login'),
    path('register/', views.Register.as_view(), name='register'),
    path('logout/', views.Logout_View, name='logout'),
    path('library-search/',views.LibrarySearch, name='library_search'),
    # path('friends_list/', views.FriendsListPage,name='friends_list_page'),
    path('friends-list/', views.FriendsListPage,name='friends_list_page'),
    path('add-a-friend/', views.AddFriend,name='add_friend'),
    path('remove-a-friend/', views.RemoveFriend,name='remove_friend'),
    path('profile/<str:username>/', views.FriendProfile,name='friend_profile'),
    path('feedback/', views.FeedbackPage, name = 'feedback'),
]