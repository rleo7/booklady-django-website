from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View, generic
from .models import CustomUser,FriendsList, Badge
from .forms import UserForm, ContactForm, FeedbackForm
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from .api_wrapper import fetch_libraries
from .utils import check_for_new_badges
import environ
from django.core.paginator import Paginator
from pynytimes import NYTAPI
from general.models import Book

env = environ.Env()
env.read_env()  # reading .env file

key = env.str('NYT_KEY')

def Home(request):
    context={}
    nyt = NYTAPI(key, parse_dates=True)
    LatestBooksCombinedFiction = nyt.best_sellers_list(name="combined-print-and-e-book-fiction", date=None)

    # Iterate over each book in LatestBooksCombinedFiction
    for book_data in LatestBooksCombinedFiction[:15]:
        rank = book_data.get("rank")
        rank_last_week = book_data.get("rank_last_week")
        author = book_data.get("author")
        title = book_data.get("title")
        description = book_data.get("description")
        amazon_product_url = book_data.get("amazon_product_url")
        
        # Create a Book instance and save it
        book_instance = Book.objects.create(
            rank=rank,
            rank_last_week=rank_last_week,
            author=author,
            title=title,
            description=description,
            amazon_product_url=amazon_product_url
        )

    context["list"] = Book.objects.all()[:15]  # Fetch only the top 15 Book instances


    return render(request, 'general/home.html',context)

def About(request):
    return render(request, 'general/about.html')

def FeedbackPage(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
        messages.success(request, 'Thank you for your feedback!')
        return redirect('home')

    else:
        form = FeedbackForm()
    return render(request, 'general/feedbackPage.html', {'form': form})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            email_message = "Name: {}\nEmail: {}\nSubject: {}\n\nMessage: {}".format(name, email, subject, message)
            email_subject = 'Contact Form Submission from {}'.format(name)

            # Sending email
            EmailMessage(
               email_subject, email_message, to=['Katewatts088@gmail.com'], reply_to=[email]
            ).send()
    else:
        form = ContactForm()
    return render(request, 'general/contactPage.html', {'form': form})


def LegalPage(request):
    return render(request, 'general/legalPage.html')

def LibrarySearch(request):
    if request.method == 'GET':
        Postcode = request.GET.get('Postcode')

        libraries=fetch_libraries(Postcode)
        context = {}

        context['libraries'] = libraries
        return render(request, 'general/librarySearch.html', context)
    else:
        return HttpResponseRedirect(reverse_lazy('home'))

@login_required
def profile(request):
    user = request.user
    badges = user.badges.all() 

    # Check for new badges and update the user's badges
    new_badges = check_for_new_badges(user)

    return render(request, 'general/profilePage.html', {'user': user, 'badges': badges, 'new_badges': new_badges})

class Register(SuccessMessageMixin, generic.edit.CreateView):
    form_class = UserForm 
    template_name = 'register.html'
    success_message = ('User Created')
    success_url = reverse_lazy('login')

def Logout_View(request):
    logout(request)
    return redirect('home')

@login_required
def FriendsListPage(request :HttpRequest):
    if not request.user.is_authenticated:
        return redirect('home')
    
    user :CustomUser = request.user
    friend_objects = user.friends_list.all().order_by("username")


    # friend_objects = user.mutual_friends().order_by("id")
    paginator = Paginator(friend_objects,10)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    obj_mutual = {}
    i = 0
    for friend_obj in page_obj:
        obj_mutual[friend_obj] = user.is_mutual_friend(friend_obj)
        i+=1

    context= { 
        "page_obj": page_obj,
        "obj_mutual": obj_mutual
    }

    return render(request, 'general/friendsListPage.html', context)

@login_required
def AddFriend(request :HttpRequest):
    if not request.user.is_authenticated:
        return redirect('home')
    
    fc = request.GET.get('friend')
    if fc is not None:     #If user is searching for friend code
        #print(fc)
        context={ "prefill_text": fc }
        try:
            target = CustomUser.objects.get(friend_code=fc)
        except CustomUser.DoesNotExist:
            messages.add_message(request, messages.WARNING, "User not found")
            return render(request, 'general/addFriend.html', context)

        context = { "target": target }
        current_user :CustomUser = request.user
        if current_user.friends_list.contains(target): #Will mute add friend button if they're already a friend
            context["is_already_friend"] = True

        return render(request, 'general/addFriend.html', context)
    

    elif request.method == 'POST':  #If user has pressed Add Friend on successful friend code search result 
        target_id = request.POST.get('target_id')
        target = CustomUser.objects.get(id=target_id)
        current_user :CustomUser = request.user
        current_user.friends_list.add(target)   #Add new friend to current user's friendlist
        target.friends_list.add(current_user)   #Add current user to new friend's friendlist

        messages.add_message(request, messages.SUCCESS, target.username + " is now your friend!")
        return render(request, 'general/addFriend.html')


    else: #If search has not been done, i.e first time opening page
        return render(request, 'general/addFriend.html')

@login_required
def RemoveFriend(request :HttpRequest):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if 'friend_id' not in request.POST:
        return HttpResponseBadRequest()
    
    user :CustomUser = request.user
    target = get_object_or_404(CustomUser, id=request.POST.get('friend_id'))

    if 'friend_deleted' in request.POST:
        user.friends_list.remove(target)
        
        return redirect("friends_list_page")
    else:
        context = { "target" : target}
        return render(request, "general/removeFriend.html",context)

def FriendProfile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    return render(request, 'general/friendsProfile.html', {'user': user})