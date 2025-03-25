from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import InviteCode, Message, Profile

# Get the custom user model
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    invite_code = forms.CharField(
        max_length=10,
        required=True,
        help_text="Enter a valid invite code to join.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Invite Code'
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "invite_code"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_invite_code(self):
        invite_code = self.cleaned_data.get("invite_code")
        if not InviteCode.objects.filter(code=invite_code, used_by__isnull=True).exists():
            raise forms.ValidationError("This invite code is invalid or has already been used.")
        return invite_code

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['password1', 'password2']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class MessageForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "placeholder": "Type your message...", 
            "rows": 4,
            "class": "form-control"
        })
    )

    class Meta:
        model = Message
        fields = ["content"]

class ProfileCoverForm(forms.ModelForm):
    cover_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control',
            'id': 'cover-image-upload'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['cover_image']

class ProfileEditForm(forms.ModelForm):
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'maxlength': 500,
            'class': 'form-control',
            'placeholder': 'Tell others about yourself...'
        })
    )
    
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control',
            'id': 'profile-image-upload'
        })
    )
    
    social_links = forms.JSONField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'profile_image', 'social_links']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True  # Prevent username changes