from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from django.db.models import Q

from general.models import CustomUser
from general.models import FriendsList
from .models import Leaderboard

##Global
def GlobalLeaderboardAlltime(request :HttpRequest):
    user_list = CustomUser.objects.all().order_by("-score") #-score orders by score in DESC order
    paginator = Paginator(user_list, 100)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'leaderboards/globalLeaderboardAlltime.html', context)

def GlobalLeaderboardMonthly(request :HttpRequest):
    user_list = Leaderboard.objects.select_related('user').all().order_by("-monthly_score")
    paginator = Paginator(user_list, 100)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'leaderboards/globalLeaderboardMonthly.html', context)


##Friends
@login_required
def FriendsLeaderboardAlltime(request :HttpRequest):
    if(not request.user.is_authenticated):  #Default to global if not logged in
        return GlobalLeaderboardAlltime(request)
    current_user :CustomUser = request.user

    friends = CustomUser.objects.filter(    #Filter gets current user and their mutual friends
        Q(id=current_user.id) |
        Q(id__in=current_user.mutual_friends())
    ).order_by("-score")
    
    paginator = Paginator(friends, 10)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'leaderboards/friendsLeaderboardAlltime.html', context)

@login_required
def FriendsLeaderboardMonthly(request :HttpRequest):
    if(not request.user.is_authenticated):  #Default to global if not logged in
        return GlobalLeaderboardAlltime(request)

    current_user :CustomUser = request.user
    friends = Leaderboard.objects.filter(   #Filter gets current user and their mutual friends
        Q(user_id=current_user.id) |
        Q(user_id__in=current_user.mutual_friends())
    ).order_by("-monthly_score")

    paginator = Paginator(friends,10)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'leaderboards/friendsLeaderboardMonthly.html', context)