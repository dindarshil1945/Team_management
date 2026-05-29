from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Team, CustomUser


admin.site.register(Team)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Team Management', {'fields': ('role', 'team')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Team Management', {'fields': ('role', 'team')}),
    )
    list_display = ('username', 'email', 'role', 'team', 'is_staff')
    list_filter = ('role', 'team', 'is_staff', 'is_superuser')
