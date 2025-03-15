from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Ensure this file exists inside templates/
