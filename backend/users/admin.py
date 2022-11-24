from django.contrib import admin, auth

from django.contrib.auth import get_user_model

from .models import Follow

admin.site.unregister(auth.models.Group)

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', )
    list_filter = ('email', 'username', )
    search_fields = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'follower',
        # 'author__username',
        # 'follower___username',
    )
    search_fields = ('author', )
