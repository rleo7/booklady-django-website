from django.test import TestCase, Client
from django.urls import reverse
from .models import Book
from django.core.exceptions import ValidationError
from unittest.mock import patch
import os

class books_Tests(TestCase):

    def setUp(self):
        return


    #test for book search webpage
    def test_bookSearch(self):
        response = self.client.get(reverse('book_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search for a Book')

    #test for invalid book title
    def test_invalid_title(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='', 
                subtitle='Subtitle',
                description='Description',
                author='Author',
                publisher='Publisher',
                published_date='01012024', 
                isbn='044091455-8',
                page_count=200, 
                rating=4,
                genre='Fiction'
            )

            book.full_clean()

    #test for invalid subtitle
    def test_invalid_subtitle(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='',
                description='Description',
                author='Author',
                publisher='Publisher',
                published_date='01012024', 
                isbn='044091455-8',
                page_count=200, 
                rating=4,
                genre='Fiction'
            )

            book.full_clean()
    
    #test for invalid description
    def test_invalid_description(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='Subtitle',
                description='',
                author='Author',
                publisher='Publisher',
                published_date='01012024', 
                isbn='044091455-8',
                page_count=200, 
                rating=4,
                genre='Fiction'
            )

            book.full_clean()

    #test for invalid author
    def test_invalid_author(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='Subtitle',
                description='Description',
                author='',
                publisher='Publisher',
                published_date='01012024', 
                isbn='044091455-8',
                page_count=200, 
                rating=4,
                genre='Fiction'
            )

            book.full_clean()

    #test for invalid publisher
    def test_invalid_publisher(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='Subtitle',
                description='Description',
                author='Author',
                publisher='',
                published_date='01012024', 
                isbn='044091455-8',
                page_count=200, 
                rating=4,
                genre='Fiction'
            )

            book.full_clean()

    #test for invalid date
    def test_invalid_date(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='Subtitle',
                description='Description',
                author='Author',
                publisher='Publisher',
                published_date='', 
                isbn='044091455-8',
                page_count=200, 
                rating=4,
                genre='Fiction'
            )

            book.full_clean()

    #test for invalid isbn
    def test_invalid_isbn(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='Subtitle',
                description='Description',
                author='Author',
                publisher='Publisher',
                published_date='01012024', 
                isbn='044091455-854-12',
                page_count=200, 
                rating=4,
                genre='Fiction'
            )

            book.full_clean()

    #test for invalid pagecount
    def test_invalid_page_count(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='Subtitle',
                description='Description',
                author='Author',
                publisher='Publisher',
                published_date='01012024', 
                isbn='044091455-8',
                page_count=5467, 
                rating=4,
                genre='Fiction'
            )

            book.full_clean()

    #test for invalid rating
    def test_invalid_rating(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='Subtitle',
                description='Description',
                author='Author',
                publisher='Publisher',
                published_date='01012024', 
                isbn='044091455-8',
                page_count=200, 
                rating=7,
                genre='Fiction'
            )

            book.full_clean()

    #test for invalid genre
    def test_invalid_genre(self):
        with self.assertRaises(ValidationError):
            book = Book.objects.create(
                title='Title', 
                subtitle='Subtitle',
                description='Description',
                author='Author',
                publisher='Publisher',
                published_date='01012024', 
                isbn='044091455-8',
                page_count=200, 
                rating=4,
                genre=''
            )

            book.full_clean()

    def test_book_search_SQL_injection(self):
        malicious = "' OR 1=1;--"
        response = self.client.get(reverse('book_search'), {'query': malicious})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/bookSearch.html')

    def test_book_list_view_api_call(self):
        #test the book list view and API call
        url = reverse('book_list')
        client = Client()

        with patch('requests.get') as mock_get:
            # simulate API response
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
            'items': [
                {
                    'volumeInfo': {
                        'title': 'Charlie and the Chocolate Factory',
                        'authors': ['Roald Dahl'],
                        'imageLinks': {'thumbnail': 'https://example.com/image.jpg'},
                        'publisher': 'Wolff, Jacobs and Ebert',
                        'publishedDate': '2019-09-16',
                        'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': '9780440914554'}],
                        'ratingsCount': 2,
                        'pageCount': 283
                    }
                },
                    
            ]
        }

            response = client.get(url, {'search': 'test'})

            mock_get.assert_called_once_with(
                'https://www.googleapis.com/books/v1/volumes',
                params={'q': 'test', 'inauthor': '', 'key': os.environ("API_KEY")}
            )

            self.assertEqual(response.status_code, 200)


    