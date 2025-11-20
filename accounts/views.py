from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import EnergyUser

class EnergyUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
    class Meta:
        model = EnergyUser
        fields = ['energy_number', 'name', 'password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class EnergyUserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Energy Number')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('energy:dashboard')
    
    if request.method == 'POST':
        form = EnergyUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.name}')
            return redirect('energy:dashboard')
    else:
        form = EnergyUserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('energy:dashboard')
    
    if request.method == 'POST':
        energy_number = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=energy_number, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Welcome {user.name}')
            return redirect('energy:dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    form = EnergyUserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('accounts:login')
