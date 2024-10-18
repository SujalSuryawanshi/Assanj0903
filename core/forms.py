from django import forms
from .models import Staller,Rating, MenuItems, FooRating,Foo_Category, New_offer
from django import forms
from rest_framework import serializers
from users.models import CustomUser


class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'}))

class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name']  # Add other fields if needed

class SignInForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email=forms.CharField(max_length=30,required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone


class StallerForm(forms.ModelForm):
    class Meta:
        model = Staller
        fields = [
           'address', 'category', 'contact',
            'timings', 'keywords','payr'
        ]


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class AddItemForm(forms.ModelForm):
    class Meta:
        model = MenuItems
        fields = ['menu_photo', 'name', 'foo_cat', 'normal_price', 'premium_price','description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class EditItem(forms.ModelForm):
    class Meta:
        model = MenuItems
        fields = ['menu_photo', 'name', 'foo_cat', 'normal_price','description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




class MenuRatingForm(forms.ModelForm):
    class Meta:
        model = FooRating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class FooCategoryForm(forms.ModelForm):
    class Meta:
        model = Foo_Category
        fields = ['foo_name'] 

class NewOfferForm(forms.ModelForm):
    class Meta:
        model=New_offer
        fields=['title','offer_photo','message']

class EditOfferForm(forms.ModelForm):
    class Meta:
        model = New_offer
        fields = ['title', 'offer_photo', 'message']



class StallerSurveyForm(forms.ModelForm):
    class Meta:
        model = Staller
        fields = ['location_accuracy', 'surrounding_landmarks', 'owner_behaviour', 'locality_preferred_for', 'locality_visited_with']
        widgets = {
            'location_accuracy': forms.NumberInput(attrs={
                'type': 'number',
                'min': 0,
                'max': 100,
                'placeholder': 'Enter accuracy (0-100%)',
                'class': 'form-control'  # You can add Bootstrap classes if needed
            }),
            'surrounding_landmarks': forms.Textarea(attrs={
                'rows': 3,
                'cols': 40,
                'class': 'form-control'  # Adding Bootstrap class for styling
            }),
            'owner_behaviour': forms.RadioSelect(choices=[
                ('bad', 'Bad'),
                ('average', 'Average'),
                ('good', 'Good'),
                ('great', 'Great')
            ]),
            'locality_preferred_for': forms.RadioSelect(choices=[
                ('family', 'Family'),
                ('friends', 'Friends'),
                ('couples', 'Couples')
            ]),
            'locality_visited_with': forms.RadioSelect(choices=[
                ('family', 'Family'),
                ('friends', 'Friends'),
                ('couples', 'Couples')
            ]),
        }

    def clean_location_accuracy(self):
        location_accuracy = self.cleaned_data.get('location_accuracy')
        if location_accuracy < 0 or location_accuracy > 100:
            raise forms.ValidationError("Location accuracy must be between 0 and 100.")
        return location_accuracy
