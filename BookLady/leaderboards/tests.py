from django.test import TestCase
from django.urls import reverse
from .models import Leaderboard, CustomUser

# Create your tests here.
class Leaderboards_URL_Tests(TestCase):

    def setUp(self):
        return

    #test for all time friends leaderboard webpage
    def test_all_time_friends(self):
            response = self.client.get(reverse('friends_alltime'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Lifetime Pages Read')

    #test for monthly friends leaderboard webpage
    def test_monthly_friends(self):
            response = self.client.get(reverse('friends_monthly'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Lifetime Pages Read')

    #test for all time global leaderboard webpage
    def test_all_time_global(self):
            response = self.client.get(reverse('global_alltime'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Lifetime Pages Read')

    #test for monthly leaderboard webpage
    def test_monthly_global(self):
            response = self.client.get(reverse('global_monthly'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Lifetime Pages Read')


class LeaderboardsModel_Tests(TestCase):
       
    def setUp(self):
        self.user = CustomUser.objects.create(
            username='testuser'
        )

    #test for the creation of the leaderboard with default values set correctly
    def test_leaderboard_creation(self):
        entry = Leaderboard.objects.create(
            user=self.user
        )
        self.assertEqual(entry.weekly_score, 0)
        self.assertEqual(entry.monthly_score, 0)

    #test that scores are updated correctly
    def test_scores_update(self):
        entry = Leaderboard.objects.create(
            user=self.user
        )
        entry.weekly_score = 48
        entry.monthly_score = 176
        entry.save()
        self.assertEqual(entry.weekly_score, 48)
        self.assertEqual(entry.monthly_score, 176)
             
              
       
