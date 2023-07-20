from django_filters.rest_framework import FilterSet, filters, CharFilter

from recipes.models import Recipe, Ingredient


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith', )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            user = self.request.user
            if user.is_authenticated:
                return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            user = self.request.user
            if user.is_authenticated:
                return queryset.filter(cart__user=user)
        return queryset
