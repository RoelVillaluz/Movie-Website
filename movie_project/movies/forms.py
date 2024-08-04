from django import forms

class searchForm(forms.Form):
    query = forms.CharField(label="Search", max_length=50)