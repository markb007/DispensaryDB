from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email address", help_text="Enter your email address",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email Address'}))
    first_name = forms.CharField(label='First name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}))
    last_name = forms.CharField(label='Last name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'User name'
        self.fields['username'].widget.attrs['placeholder'] = 'Enter User Name'
        self.fields['username'].help_text = \
            '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['email'].help_text = \
            '<span class="form-text text-muted"><small>Required. Enter email address.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter Password'
        self.fields['password1'].help_text = '''<span class="form-text text-muted"><small><ul> 
             <li>Your password can\'t be too similar to your other personal information.</li> 
             <li>Your password must contain at least 8 characters.</li>    
             <li>Your password can\'t be a commonly used password.</li>    
             <li>Your password can\'t be entirely numeric.</li></ul></small></span>'''
            
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].help_text = \
            '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
