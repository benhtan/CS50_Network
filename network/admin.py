from django.contrib import admin
from .models import User, Post

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')

admin.site.register(User,UserAdmin)

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post_content', 'created_timestamp', 'edited_timestamp')

admin.site.register(Post,PostAdmin)