from django.db import models
from django.core.validators import MaxValueValidator
from general.models import CustomUser


##TODO: Review if reasonable to convert published_date to DateField when importing from API (allowing date sorting)
##      If done, seed.py will need to be edited
class Book(models.Model):
    title = models.CharField(max_length = 200) 
    subtitle = models.CharField(max_length = 100)
    description = models.CharField(max_length = 1000)
    author = models.CharField(max_length = 100) # If there are multiple authors, these will be entered as one string
    publisher = models.CharField(max_length = 100)
    published_date = models.CharField(max_length = 10) # DD-MM-YYYY, without the dashes
    isbn = models.CharField(max_length = 15, primary_key=True) 
    page_count = models.IntegerField(default = 0, validators=[MaxValueValidator(4000)])
    rating = models.PositiveIntegerField(default = 0, validators=[MaxValueValidator(5)]) # Ratings to be no greater than 5
    genre = models.CharField(max_length = 50) # volumeInfo.mainCategory

    def __str__(self):
        return self.title

# A review will be related to an ISBN, not a Book object.
class BookReview(models.Model):
    RATINGS = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    isbn = models.CharField(max_length=50)
    review = models.TextField()
    rating = models.IntegerField(choices=RATINGS, default=None)
    date = models.DateTimeField(auto_now_add=True)
