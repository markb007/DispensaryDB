from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .forms import SignUpForm
from django.contrib import messages


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, ('Registration complete !!!'))
            return redirect('home')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)
