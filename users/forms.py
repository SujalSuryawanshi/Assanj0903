from django import forms
from .models import CustomUser

class UserSearchForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)

    def search(self):
        username = self.cleaned_data['username']
        return CustomUser.objects.filter(username__icontains=username)
    
