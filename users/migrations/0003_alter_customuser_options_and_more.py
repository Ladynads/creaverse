# Generated by Django 5.1.7 on 2025-03-25 04:23

import django.core.validators
import django.db.models.deletion
import users.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_comment_post_remove_comment_user_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['-date_joined'], 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterField(
            model_name='customuser',
            name='profile_image',
            field=models.ImageField(blank=True, help_text='Upload a profile picture (1:1 aspect ratio recommended)', null=True, upload_to=users.models.upload_to_profile_pics, validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='social_links',
            field=models.JSONField(blank=True, default=dict, help_text="Social media links in JSON format (e.g., {'twitter': 'https://...'})"),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover_image', models.ImageField(blank=True, help_text='Upload a cover image (recommended size: 1500x500px)', null=True, upload_to='cover_images/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])])),
                ('location', models.CharField(blank=True, help_text="User's location", max_length=100, null=True)),
                ('website', models.URLField(blank=True, help_text='Personal website URL', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
            },
        ),
    ]
