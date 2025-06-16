from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('search/', views.bookSearchView, name = 'book_search'),
    path('list/', views.bookListView, name = 'book_list'),
    path('account/', views.AccountView, name='account'),
    path('detail/', views.bookDetailView, name = 'book_detail'),
    path('update-score/', views.update_score, name='update_score'),
    path('book_read/',views.bookRead,name='book_read'),
]