from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views import View

# ✅ User Registration View
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in automatically
            return redirect('home')  # Redirect to homepage after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# ✅ Login View
class CustomLoginView(LoginView):
    template_name = 'users/login.html'

# ✅ Logout View (Allows only POST request)
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')  # Redirect after logout

    def post(self, request, *args, **kwargs):
        """Logout user on POST request (More secure)"""
        logout(request)
        return redirect(self.next_page)
