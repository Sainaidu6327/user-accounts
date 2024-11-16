from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from .forms import UsernameChangeForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user first
            
            # Check if the user already has a profile
            if not hasattr(user, 'profile'):
                profile = Profile(user=user)  # Create a Profile for the new user
                profile.save()  # Save the profile
                
            messages.success(request, 'Account created successfully.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})



def user_login(request):  
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  
                messages.success(request, "You are now logged in.")
                return redirect('index')  
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please enter both fields.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    # Ensure the user has a profile
    if not hasattr(request.user, 'profile'):
        profile = Profile(user=request.user)
        profile.save()

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'accounts/profile.html', {'profile_form': profile_form})

            
def index(request):
    username = request.user.username
    return render(request, 'accounts/index.html',{'username': username})

def user_logout(request):
    logout(request)  # Logs out the user
    return redirect('login') 

def user_list(request):
    users = User.objects.all().order_by('date_joined')  # Order by the registration date
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def delete_user(request, user_id):
    # Check if the logged-in user is 'sk' (superuser)
    if request.user.username != 'sai':
        messages.error(request, "You do not have permission to delete users.")
        return redirect('user_list')

    user_to_delete = get_object_or_404(User, pk=user_id)

    # Prevent 'sk' from deleting their own account
    if request.user == user_to_delete:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')

    # Allow deletion for any other user
    user_to_delete.delete()
    messages.success(request, f"User {user_to_delete.username} has been deleted successfully.")
    return redirect('user_list')



@login_required
def change_username(request):
    if request.user.is_superuser:
        messages.error(request, "Admins cannot change their username.")
        return redirect('profile')  # Redirect to profile page for admins
    if request.method == 'POST':
        form = UsernameChangeForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['new_username']
            user = request.user
            user.username = new_username
            user.save()
            messages.success(request, "Username updated successfully!")
            return redirect('profile')  # Redirect to profile page after update
    else:
        form = UsernameChangeForm()

    return render(request, 'accounts/change_username.html', {'form': form})
