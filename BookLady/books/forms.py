from django import forms
from .models import BookReview


class BookSearch(forms.Form):
    search = forms.CharField(
        label="Search for a book", required=False, widget=forms.TextInput(attrs={'class': "field__input", 'id': 'search', 'autofocus': True}))
    isbn = forms.CharField(
        label="Search by isbn", required=False, widget=forms.TextInput(attrs={'class': "field__input", 'id': 'isbn'}))
    
class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['review', 'rating']

    def __init__(self, *args, **kwargs):
        super(BookReviewForm, self).__init__(*args, **kwargs)

        self.fields['review'].widget.attrs['placeholder'] = 'Write your review here'
        self.fields['rating'].widget.attrs['class'] = 'form-control'