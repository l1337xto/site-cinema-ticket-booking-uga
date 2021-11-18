from django import forms
from django.forms import Form, ModelForm, DateField, widgets, TextInput, EmailInput
from .models import *

class MovieSearchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = False   
    class Meta:
        model = Movies
        fields = ['title', 'genre']
        required = ['title', 'genre']
        labels = {'title': 'Movie Name', 'genre':'Category'}
        widgets = {
            'title' : widgets.TextInput(attrs={'placeholder': 'Movie Name', 'class':'form-control','style': 'width: 300px;','color':'black'}),
            'genre' : widgets.Select(attrs={'placeholder':'Category','class' : 'form-control','style':'width: 160px'})
        }