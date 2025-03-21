from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, InviteCode, Message

class CustomUserCreationForm(UserCreationForm):
    invite_code = forms.CharField(max_length=10, required=True, help_text="Enter a valid invite code to join.")

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "invite_code"]

    def clean_invite_code(self):
        invite_code = self.cleaned_data.get("invite_code")
        if not InviteCode.objects.filter(code=invite_code, used_by__isnull=True).exists():
            raise forms.ValidationError("This invite code is invalid or has already been used.")
        return invite_code

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]  # Only allow sending message content

        widgets = {
            "content": forms.Textarea(attrs={"placeholder": "Type your message...", "rows": 4})
        }
