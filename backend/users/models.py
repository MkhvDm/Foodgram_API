from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user with required fields."""

    email = models.EmailField(
        'email',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField('first name', max_length=150, blank=False)
    last_name = models.CharField('last name', max_length=150, blank=False)

    # objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_staff

    def __str__(self):
        return self.username
