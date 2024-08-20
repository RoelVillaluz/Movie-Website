from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(
        label="Search",
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search movies...'
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
        ('review_count_asc', 'Reviews (Most First)'),
        ('review_count_desc', 'Reviews (Least First)'),
        ('runtime_asc', 'Runtime (Shortest First)'),
        ('runtime_desc', 'Runtime (Longest First)'),
    ]

    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label="Sort by")
