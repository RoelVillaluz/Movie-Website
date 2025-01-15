from django import forms

from movies.models import MovieImage, PersonImage, Review

class SearchForm(forms.Form):
    query = forms.CharField(
        label="Search",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search'
        })
    )

class MovieSortForm(forms.Form):
    SORT_CHOICES = [
        ('title_asc', 'Title (A-Z)'),
        ('title_desc', 'Title (Z-A)'),
        ('rating_asc', 'Rating (Lowest First)'),
        ('rating_desc', 'Rating (Highest First)'),
        ('release_date_asc', 'Release Date (Oldest First)'),
        ('release_date_desc', 'Release Date (Newest First)'),
        ('popularity', 'Popularity'),
        ('runtime_asc', 'Runtime (Shortest First)'),
        ('runtime_desc', 'Runtime (Longest First)'),
    ]

    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label="Sort by")

class MovieImageForm(forms.ModelForm):
    class Meta:
        model = MovieImage
        fields = ['image', 'actors', 'directors']
    
    def __init__(self, *args, **kwargs):
        super(MovieImageForm, self).__init__(*args, **kwargs)
        self.fields["image"].required = True

class PersonImageForm(forms.ModelForm):
    class Meta:
        model = PersonImage

        fields = ['image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review

        fields = ['description', 'rating']