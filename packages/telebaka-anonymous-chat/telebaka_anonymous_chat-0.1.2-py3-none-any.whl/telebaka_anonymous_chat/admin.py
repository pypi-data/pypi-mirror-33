from django.contrib import admin

from telebaka_anonymous_chat.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
