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

    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    # objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_staff

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок пользователей друг на друга."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='followers'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follows'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
