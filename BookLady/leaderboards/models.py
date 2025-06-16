from django.db import models
from general.models import CustomUser

class Leaderboard(models.Model):
    user=models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True
    )
    monthly_score=models.PositiveIntegerField(default=0)