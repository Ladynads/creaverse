from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    invite_code = forms.CharField(max_length=10, required=False, help_text="Enter your invite code (optional).")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'profile_image', 'invite_code']

    def clean_invite_code(self):
        code = self.cleaned_data.get('invite_code')
        if code and not CustomUser.objects.filter(invite_code=code).exists():
            raise forms.ValidationError("Invalid invite code.")
        return code
