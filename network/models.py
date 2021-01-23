from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import related
from django.forms import ModelForm, Textarea


class User(AbstractUser):
    following = models.ManyToManyField('self', blank=True, related_name='followers', symmetrical=False)
    def __str__(self):
        return f"{self.id}: {self.username}"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_content = models.TextField(max_length=280)
    likes = models.ManyToManyField(User, blank=True, related_name='user_likes')
    created_timestamp = models.DateTimeField(auto_now_add=True)
    edited_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.post_content}"

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['post_content']
        label = {
            'post_content': 'Post'
        }
        widgets = {
            'post_content': Textarea(attrs={'class': 'form-control', 'placeholder': 'What\'s on your mind?', 'style': 'height: 5em; width: 100%;'}),
        }
