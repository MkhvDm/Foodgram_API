from django.contrib import admin, auth

from .models import User

admin.site.unregister(auth.models.Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username',)
