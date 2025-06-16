import json
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from general.models import CustomUser, FriendsList, ScheduledTasks
from books.models import Book
from leaderboards.models import Leaderboard

SAMPLE_DIR = settings.BASE_DIR / "sample_data"

DATE_FORMAT = '%Y-%m-%d'

class Command(BaseCommand):
    def handle(self, *args, **options):
        CustomUser.objects.all().delete()
        Book.objects.all().delete()
        Leaderboard.objects.all().delete()
        ScheduledTasks.objects.all().delete()
        
        assert not FriendsList.objects.all()


        user_friends_lists :dict[int,list[str]] = {}

        ### Seeding users
        if "users" in args or not args:
            print("seeding users")
            with open(SAMPLE_DIR / "users.json") as user_json_file:
                users_json = json.load(user_json_file)

                for user_dict in users_json['users']:
                    temp :list[str] = user_dict['friends_list']
                    #user_friends_lists[user.id] = list(user_dict['friends_list'])

                    del user_dict['friends_list']
                    user=CustomUser(**user_dict)
                    user.set_password(user_dict['password'])

                    user.save()
                    user_friends_lists[user.id] = temp

            
            ### Seeding friends
                for user in CustomUser.objects.all():
                    for friend_username in user_friends_lists[user.id]:
                        friend = CustomUser.objects.get(username=friend_username)
                        user.friends_list.add(friend)

        if "books" in args or not args:
        ### Seeding books
            print("seeding books")
            with open(SAMPLE_DIR / "books.json") as books_json_file:
                books_json = json.load(books_json_file)

                for book_dict in books_json['books']:
                    ##TODO: ONLY uncomment below code if published_date becomes DateField
                    #book_dict['published_date'] = datetime.datetime.strptime(book['published_date'],DATE_FORMAT).date()

                    book=Book(**book_dict)
                    book.save()
        
        if "leaderboard" in args or not args:
            print("seeding leaderboard")
            ### Seeding leaderboard
            # with open(SAMPLE_DIR / "leaderboard.json") as leaderboard_json_file:
            #     leaderboard = json.load(leaderboard_json_file)

            #     for leaderboard_dict in leaderboard:
            #         placement=Leaderboard(**leaderboard_dict)
            #         placement.save()
            with open(SAMPLE_DIR / "leaderboard.json") as leaderboard_json_file:
                lb_json :dict[str,int] = json.load(leaderboard_json_file)
                print(lb_json)

                for u_name, m_score in lb_json.items():
                    lb_dict = {
                        "user": CustomUser.objects.get(username=u_name),
                        "monthly_score": m_score
                    }
                    lb_obj = Leaderboard(**lb_dict)
                    lb_obj.save()
        
        ##TODO: Choose how to seed friends (no homo)