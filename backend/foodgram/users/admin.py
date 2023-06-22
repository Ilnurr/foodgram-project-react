from django.contrib import admin

from .models import  User, Subscribed

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username','email')
    list_filter = ('username','email')

@admin.register(Subscribed)
class Subscribedadmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
