from django.conf.urls import url
from django.shortcuts import render
from django.shortcuts import redirect,render
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm,UserUpdateForm


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successfull')
            return redirect('login')
        else:
            return render(request, "accounts/register.html",{'form':form})
    else:
        form = RegisterForm()
        return render(request, "accounts/register.html",{'form':form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request,user)
            messages.success(request, 'Login successful')
            return redirect(request.session['next'])
        else:
            return render(request, "accounts/login.html")
    else:
        request.session['next'] = request.GET.get('next','/')
        return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('login')


@login_required
def home(request):
    return render(request, "accounts/index.html")


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            messages.success(request,'Profile updated successfully')
            return redirect(request.path)
        else:
            return render(request,"accounts/edit_profile.html",{'form':form})
    else:
        form = UserUpdateForm(instance = request.user)
        return render(request, "accounts/edit_profile.html",{'form':form})
