from django.contrib import admin # type: ignore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # type: ignore
from users.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass
