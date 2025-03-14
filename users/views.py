from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm

# User Registration View
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Custom Login View
class CustomLoginView(LoginView):
    template_name = 'users/login.html'

# Custom Logout View - Allow Logout via GET
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')  # Redirect to home after logout

    def get(self, request, *args, **kwargs):
        """Allow logout via GET request"""
        logout(request)  # Explicitly logout the user
        return redirect(self.next_page)  # Redirect user after logout