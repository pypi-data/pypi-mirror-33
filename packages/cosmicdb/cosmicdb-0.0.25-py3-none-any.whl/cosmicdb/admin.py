from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from cosmicdb.models import UserSystemMessage, UserSystemNotification


class UserSystemMessageInlineAdmin(admin.TabularInline):
    model = UserSystemMessage


class UserSystemNotificationInlineAdmin(admin.TabularInline):
    model = UserSystemNotification


class UserProfileAdmin(UserAdmin):
    inlines = [
        UserSystemMessageInlineAdmin,
        UserSystemNotificationInlineAdmin,
    ]


user_model = get_user_model()
admin.site.register(user_model, UserProfileAdmin)
