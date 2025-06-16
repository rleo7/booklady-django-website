from django.test import TestCase, Client
from django.urls import reverse
from.models import CustomUser, FriendsList
from django.core.exceptions import ValidationError
from unittest.mock import patch
from .models import Book
from .api_wrapper import fetch_libraries


class general_URL_Tests(TestCase):

    def setUp(self):
        return

    #test for about us webpage
    def test_about(self):
            response = self.client.get(reverse('about'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'About Page')

    #test for contact us webpage
    def test_contact(self):
            response = self.client.get(reverse('contact_page'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Contact Page')

    #test for home webpage
    def test_home(self):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Home Page')

    #test for legal webpage
    def test_legal_page(self):
            response = self.client.get(reverse('legal_page'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Legal Page')

    #test for user homepage
    def test_user_home(self):
            response = self.client.get(reverse('user_home'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Home')
            
    #test for login webpage
    def test_login_page(self):
            response = self.client.get(reverse('login'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Log In')
    
    #test for register webpage
    def test_register_page(self):
            response = self.client.get(reverse('register'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Register')

class CustomUser_Tests(TestCase):
       
    def setUp(self):
        return
       
    #test for the creation of a user
    def test_user_creation(self):
        user = CustomUser.objects.create(
            username='testuser',
            password='Password123!',
            email='test@example.com',
            first_name='John',
            last_name='Smith',
            friend_code='1',
            score='73',
            lifetime_pages_read='6179',
            lifetime_books_read='45',
        )
        self.assertEqual(str(user), 'testuser')

    #test for invalid username
    def test_invalid_username(self):
        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create(
                username='',
                password='Password123!',
                email='test@example.com',
                first_name='John',
                last_name='Smith',
                friend_code='1',
                score='73',
                lifetime_pages_read='6179',
                lifetime_books_read='45',
            )
            user.full_clean()

    #test for invalid password
    def test_invalid_password(self):
        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create(
                username='testuser',
                password='',
                email='test@example.com',
                first_name='John',
                last_name='Smith',
                friend_code='1',
                score='73',
                lifetime_pages_read='6179',
                lifetime_books_read='45',
            )
            user.full_clean()

    #test for invalid email
    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create(
                username='testuser',
                password='Password123!',
                email='testexample.com',
                first_name='John',
                last_name='Smith',
                friend_code='1',
                score='73',
                lifetime_pages_read='6179',
                lifetime_books_read='45',
            )
            user.full_clean()

    def test_custom_login_SQL_inection(self):
        malicious = {
            'username': "'; DROP TABLE users; --",
            'password': 'password', 
        }
        response = self.client.post(reverse('login'), data=malicious)
        self.assertEqual(response.status_code, 200)

    def test_register_view(self):
        
        malicious = {
            'username': "'; DROP TABLE users; --",
            'password': 'password', 
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Smith',
        }
        response = self.client.post(reverse('register'), data=malicious)
        self.assertEqual(response.status_code, 200)

class FriendsList_Tests(TestCase):
      
    def setUp(self):
        self.user1=CustomUser.objects.create(
            username='testuser',
            password='Password123!',
            email='test@example.com',
            first_name='John',
            last_name='Smith',
            friend_code='1',
            score='73',
            lifetime_pages_read='6179',
            lifetime_books_read='45',
        )
        self.user2=CustomUser.objects.create(
            username='testuser2',
            password='Password567!',
            email='test2@example.com',
            first_name='Jack',
            last_name='Willis',
            friend_code='3',
            score='56',
            lifetime_pages_read='4533',
            lifetime_books_read='37',
        )

    #test firends list creation
    def test_friends_list_creation(self):
        friends_list = FriendsList.objects.create(
            user=self.user1,
            friend=self.user2
        )
        self.assertEqual(friends_list.user, self.user1)
        self.assertEqual(friends_list.friend, self.user2)

    #test for the firends list unique constraint which prevents duplicates  
    def test_unique_constraint(self):
         with self.assertRaises(Exception):
            FriendsList.objects.create(
                user=self.user1,
                friend=self.user2
            )
            FriendsList.objects.create(
                user=self.user1,
                friend=self.user2
            )

class TestHomeViewAPICall(TestCase):
    def test_home_view_api_call(self):
        #test the Home view and API call
        url = reverse('home')
        client = Client()

        with patch('general.views.NYTAPI.best_sellers_list') as mock_best_sellers_list:
            #simulate API response
            mock_best_sellers_list.return_value = [
                {
                    'rank': 1,
                    'rank_last_week': 2,
                    'author': 'Author Name',
                    'title': 'Book Title',
                    'description': 'Book Description',
                    'amazon_product_url': 'https://www.amazon.com/book-url'
                }
            ]

            response = client.get(url)

            mock_best_sellers_list.assert_called_once_with(name="combined-print-and-e-book-fiction", date=None)

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'general/home.html')
            self.assertQuerysetEqual(response.context['list'], Book.objects.all(), transform=lambda x: x)

class LibrarySearchTestCase(TestCase):
    
    def test_fetch_libraries_success(self):
        with patch('requests.get') as mock_get:

            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"name": "Library 1", "address": "Address 1"},
                {"name": "Library 2", "address": "Address 2"}
            ]

            libraries = fetch_libraries("GU2 9TH")

            self.assertEqual(len(libraries), 2)
            self.assertEqual(libraries[0]['name'], "Library 1")
            self.assertEqual(libraries[1]['address'], "Address 2")

    def test_fetch_libraries_error(self):
        with patch('requests.get') as mock_get:

            mock_response = mock_get.return_value
            mock_response.status_code = 404

            libraries = fetch_libraries("GU2 9TH")

            self.assertIsNone(libraries)
