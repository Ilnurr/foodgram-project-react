from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    '''Модель тегов'''
    name = models.CharField(
        max_length=200,
        db_index=True,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в НЕХ'
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Модель ингридиентов'''
    name = models.CharField(
        verbose_name='Название ингридиентов',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Модель рецептов'''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='autor',
        verbose_name='Recipe author'
    )
    text = models.TextField(
        verbose_name='Text'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientRecipe'
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        unique=True,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        default=None
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='Tags',
        verbose_name='Тэги рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ingred',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (f'{self.ingredient.name} - '
                f'{self.amount} {self.ingredient.measurement_unit}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='избранный recipe'
    )

    class Meta:
        verbose_name = 'Избранный рецепы'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Покупка'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
