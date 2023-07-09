from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''Модель пользователя'''
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriber(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписан',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Мои подписки'
        unique_together = ('user', 'author')

    def __str__(self):
        return 'Подписка пользователя {} на автора {}'.format(
            self.user.username, self.author.username
        )
