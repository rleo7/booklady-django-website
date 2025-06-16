from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from general.models import CustomUser
from books.models import Book, BookReview
from books.forms import BookSearch, BookReviewForm
import requests
import environ
from django.contrib.auth.decorators import login_required
from django.urls import reverse

import datetime
from typing import Any

env = environ.Env()
env.read_env()  # reading .env file

key = env.str('API_KEY')
NYT_key = env.str('NYT_KEY')

# To be Done
def AccountView(request):
    pass

# Render's the Search Page, with the form.
def bookSearchView(request):
    form = BookSearch()
    return render(request, 'books/bookSearch.html', {'form': form})

def bookListView(request):
    # Get data from form
    isbn = request.GET.get('isbn', "")
    search = request.GET.get('search', "")

    # Redirect to search page if no valid data entered
    if not search and not isbn:
        return redirect('book_search')

    # Fill the data for the Google Books Request
    queries = {'key': key}

    # If searching by ISBN
    if isbn:
        queries['q'] = "isbn:" + isbn

    # If searching by title
    elif search:
        queries['q'] = search

    # If searching by author alone, include an empty string for the title
    
    r = requests.get('https://www.googleapis.com/books/v1/volumes', params=queries)
    print(r.url)
    # If Google Books cannot be reached, return an error message
    if r.status_code != 200:
        return render(request, 'books/bookList.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})


    # Data Retrieved
    data = r.json()

    # If no books are found, return an error message
    if 'items' not in data:
        return render(request, 'books/bookList.html', {'message': 'Sorry, no books match that search term.'})

    # Create a dictionary to store books grouped by title
    title_dict = {}

    # Group books by title
    for book in data['items']:
        title = book['volumeInfo']['title']
        if title not in title_dict:
            title_dict[title] = []
        title_dict[title].append(book)

    # Create an empty list to store unique books
    unique_books = []

    # Iterate over the grouped books
    for title, books in title_dict.items():
        # Sort books by popularity (most to least)
        books.sort(reverse=True, key=lambda x: x['volumeInfo'].get('ratingsCount', 0))
        # Select the most relevant book (e.g., with the highest popularity)
        selected_book = books[0]
        # Extract information from the selected book
        isbn = None
        identifiers = selected_book['volumeInfo'].get('industryIdentifiers', [])
        for identifier in identifiers:
            if identifier['type'] == 'ISBN_13':
                isbn = identifier['identifier']
                break  # Stop after finding the first ISBN_13
        book_dict = {
            'title': title,
            'image': selected_book['volumeInfo'].get('imageLinks', {}).get('thumbnail', ""),
            'authors': ", ".join(selected_book['volumeInfo'].get('authors', [])),
            'publisher': selected_book['volumeInfo'].get('publisher', ""),
            'publishedDate': selected_book['volumeInfo'].get('publishedDate', ""),
            'isbn': isbn,
            'popularity': selected_book['volumeInfo'].get('ratingsCount', 0)
        }
        unique_books.append(book_dict)

    # Sort unique books by popularity (most to least)
    unique_books.sort(reverse=True, key=lambda x: x['popularity'])

    return render(request, 'books/bookList.html', {'books': unique_books})

def bookDetailView(request):
    if request.method == 'POST':
        # Handle review submission
        form = BookReviewForm(request.POST)
        if form.is_valid():
            isbn = request.POST.get('isbn') 
            review = form.cleaned_data['review']
            rating = form.cleaned_data['rating']
            user = request.user 
            BookReview.objects.create(user=user, isbn=isbn, review=review, rating=rating)
            redirect_url = reverse('book_detail') + '?isbn=' + isbn
            return HttpResponseRedirect(redirect_url)
    else:
        # Fetch book details
        original_isbn = request.GET.get('isbn') 
        queries = {'q': f'isbn:{original_isbn}', 'key': key}
        r = requests.get('https://www.googleapis.com/books/v1/volumes', params=queries)
        if r.status_code != 200:
            return render(request, 'books/bookList.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})
        
        data = r.json()
        fetched_books = data.get('items', [])
        books = []
        book :dict[str,dict[str,Any]]
        for book in fetched_books:
            identifiers = book['volumeInfo'].get('industryIdentifiers', [])
            isbn_13 = None
            isbn_10 = None
            for identifier in identifiers:
                if identifier['type'] == 'ISBN_13':
                    isbn_13 = identifier['identifier']
                elif identifier['type'] == 'ISBN_10':
                    isbn_10 = identifier['identifier']
            if isbn_13 and isbn_10:
                isbn = f"{isbn_13} / {isbn_10}"
            elif isbn_13:
                isbn = isbn_13
            elif isbn_10:
                isbn = convert_isbn_10_to_13(isbn_10)
            else:
                isbn = None
            book_dict = {
                'title': book['volumeInfo']['title'],
                'image': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "",
                'authors': ", ".join(book['volumeInfo']['authors']) if 'authors' in book['volumeInfo'] else "",
                'publisher': book['volumeInfo']['publisher'] if 'publisher' in book['volumeInfo'] else "",
                'publishedDate': book['volumeInfo']['publishedDate'] if 'publisher' in book['volumeInfo'] else datetime.datetime(1960,1,1,tzinfo=datetime.timezone.utc),
                'isbn': isbn,
                'popularity': book['volumeInfo']['ratingsCount'] if 'ratingsCount' in book['volumeInfo'] else 0,
                'length': book['volumeInfo']['pageCount'] if 'pageCount' in book['volumeInfo'] else 0
            }
            books.append(book_dict)
        form = BookReviewForm(initial={'isbn': original_isbn}) 
        
        # Retrieve existing reviews for the book using the original ISBN format
        reviews = BookReview.objects.filter(isbn=original_isbn)
        
        # Retrieve the number of pages read for this book from session
        pages_read_session_key = f'pages_read_{original_isbn}'
        pages_read = request.session.get(pages_read_session_key, 0)

    return render(request, 'books/bookDetail.html', {'books': books, 'form': form, 'reviews': reviews, 'pages_read': pages_read})

def convert_isbn_10_to_13(isbn_10):
    if len(isbn_10) != 10:
        return None
    
    # Remove hyphens and prefix '978' to convert ISBN-10 to ISBN-13
    isbn_13 = '978' + isbn_10[:-1]

    # Calculate the check digit for ISBN-13
    check_digit = sum((int(digit) * (3 if i % 2 else 1)) for i, digit in enumerate(isbn_13)) % 10
    check_digit = (10 - check_digit) % 10

    return isbn_13 + str(check_digit)

@login_required
def update_score(request):
    mult=1.5
    api_url = "http://|api_url|/api/fab/v3/book/"   
    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        pages_read = int(request.POST.get('pages_read'))

        # Retrieve the user
        user :CustomUser = request.user

        # Retrieve the number of pages previously read for this book from session
        pages_read_session_key = f'pages_read_{isbn}'
        previous_pages_read = request.session.get(pages_read_session_key, 0)

        # Ensure the submitted number of pages read is greater than previous
        if pages_read > previous_pages_read:
            # Update the user's score based on the number of pages read
            user.lifetime_pages_read += (pages_read - previous_pages_read)
            pages=pages_read-previous_pages_read
            lexile_score = get_lexile_score(api_url, isbn)
            if lexile_score is not None:
                print("Lexile Score:", lexile_score)
                mult=pages*lexile_score/1000
            else:
                print("Failed to fetch Lexile score.")
            user.score+=pages*mult
            

            queries = {'q': f'isbn:{isbn}', 'key': key}
            r = requests.get('https://www.googleapis.com/books/v1/volumes', params=queries)
            if r.status_code != 200:
                return render(request, 'books/bookList.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})
            
            data = r.json()
            fetched_books = data.get('items', [])
            book = fetched_books[0]
            
            
            # Update the lifetime books read count
            book_length = book['volumeInfo']['pageCount'] if 'pageCount' in book['volumeInfo'] else 0
            print(book_length)

            # Update the session data with the new number of pages read
            request.session[pages_read_session_key] = pages_read

            # Save the updated user
            user.save()

        # Redirect to the page that we came from
        isbn = request.POST.get('isbn') 
        redirect_url = reverse('book_detail') + '?isbn=' + isbn
        return HttpResponseRedirect(redirect_url)

def get_lexile_score(api_url, isbn):
    print(api_url)
    params = {
        "format": "json",
        "ISBN": isbn
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        book_info = response.json()
        lexile_score = book_info.get("lexile_score")  # Assuming the key for lexile_score is "lexile_score"
        return lexile_score
    except requests.exceptions.RequestException as e:
        print("Error fetching Lexile score:", e)
        return None
@login_required
def bookRead(request):
    # Retrieve the user
    user = request.user
    user.lifetime_books_read += 1
    user.score+=75
    user.save()
    # Redirect to home page or the current book page is we have the isbn for it
    isbn = request.POST.get('isbn') 
    if isbn is not None:
        redirect_url = reverse('book_detail') + '?isbn=' + isbn
    else:
        redirect_url = reverse('home')  
    return HttpResponseRedirect(redirect_url)


