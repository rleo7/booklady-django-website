from django.db import models
from django.contrib.auth.models import AbstractUser
from BookLady.managers import CustomUserManager
from django.utils import timezone
import random

# from typing_extensions import self
class Badge(models.Model):
    description = models.CharField(max_length=255)
    target_books = models.PositiveIntegerField()
    target_pages = models.PositiveIntegerField()
    image = models.ImageField(default='badges/lockedBadge.png')

    def __str__(self):
        return self.description


def generate_unique_code():
    while True:
        # Generate a random 10-digit number
        code = random.randint(1000000000, 9999999999)
        # Check if the generated code already exists in the database
        if not CustomUser.objects.filter(friend_code=code).exists():
            return code
        
class Book(models.Model):
    rank = models.BigIntegerField(10)
    rank_last_week = models.BigIntegerField(10)
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=130)
    description = models.CharField(max_length=1000)
    amazon_product_url = models.CharField(max_length=100)

class Feedback(models.Model):
    RATING_CHOICES = (
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars'),
        (6, '6 stars'),
        (7, '7 stars'),
        (8, '8 stars'),
        (9, '9 stars'),
        (10, '10 stars'),
    )

    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class CustomUser(AbstractUser):  # Extend django User model https://docs.djangoproject.com/en/5.0/topics/auth/default/
    objects = CustomUserManager()
    score = models.PositiveIntegerField(default = 0) #Assumes score should never go under 0
    lifetime_pages_read = models.IntegerField(default = 0)
    lifetime_books_read = models.IntegerField(default = 0)

    friend_code = models.IntegerField(default = generate_unique_code, unique = True)
    friends_list = models.ManyToManyField("self", through="FriendsList", blank=True)

    badges=models.ManyToManyField(Badge, blank=True)

    # Daily streak & calculations
    last_login = models.DateTimeField(null=True, blank=True)

    @property
    def daily_streak(self):
        if not self.last_login:
            return 0

        today = timezone.now().date()
        last_login_date = self.last_login.date()

        if last_login_date == today:
            return self._calculate_streak(today)
        elif last_login_date == today - timezone.timedelta(days=1):
            return self._calculate_streak(last_login_date)
        else:
            return 0

    def _calculate_streak(self, start_date):
        streak = 1
        current_date = start_date - timezone.timedelta(days=1)

        while True:
            if self.last_login.date() == current_date:
                streak += 1
                current_date -= timezone.timedelta(days=1)
            else:
                break

        return streak

    def __str__(self):
        return self.username
    
    def mutual_friends(self):
        moots = []
        friend :CustomUser
        for friend in self.friends_list.all():
            if friend.friends_list.contains(self):
                moots.append(friend.id)
        
        return CustomUser.objects.filter(id__in=moots)
    
    def is_mutual_friend(self,friend: 'CustomUser'):
        return self.friends_list.contains(friend) and friend.friends_list.contains(self)



class FriendsList(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name = 'friends_list_owner')
    friend=models.ForeignKey(CustomUser,on_delete=models.CASCADE)

    class Meta:
        constraints = [ #Stops a user friending a different user twice
            models.UniqueConstraint(fields=["user", "friend"],name="unique_composite")
        ]


from datetime import datetime
from datetime import timezone as dt_tz
class ScheduledTasks(models.Model):
    task = models.CharField(max_length=36, unique=True)
    last_executed = models.DateTimeField(default=datetime(2020,1,1,0,0,tzinfo=dt_tz.utc))
    last_execution_successful = models.BooleanField(default=True)