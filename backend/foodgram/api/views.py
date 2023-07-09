from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import Subscriber

from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingListSerializer, SubscribeSerializer,
                          TagSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=['post'],
        url_name='subscribe',
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user

        if not request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, contextадф={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscriber.objects.bulk_create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user
        Subscriber.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_name='subscriptions',
        url_path='subscriptions'
    )
    def subscriptions(self, request, pk=None):
        user = request.user
        queryset = Subscriber.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            context={'request': request},
            many=True,)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('is_favorited', 'author', 'tags', 'is_in_shopping_cart')
    paginator_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Recipe.objects.all()

        queryset = Recipe.objects.annotate(
            is_favorited=Exists(Favorite.objects.filter(
                user=user, recipe_id=OuterRef('id'))),
            is_in_shopping_cart=Exists(ShoppingList.objects.filter(
                user=user, recipe_id=OuterRef('id')))
        )
        return queryset

    def create_shopping_list_file(user):
        shopping_list = ShoppingList.objects.filter(user=user)
        ingredients = IngredientRecipe
        for item in shopping_list:
            for ingredient in item.recipe.ingredients.all():
                if ingredient.name in ingredients:
                    ingredients[ingredient.name] += ingredient.amount
                else:
                    ingredients[ingredient.name] = ingredient.amount
        output = ''
        for name, amount in ingredients.items():
            output += f'{name} - {amount} {ingredient.measurement_unit}\n'
        return output

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeSerializer

    def create_favorite(self, user, recipe):
        return Favorite.objects.create(user=user, recipe=recipe)

    def create_shopping_list(self, user, recipe):
        shopping_list, created = ShoppingList.objects.get_or_create(
            user=user, recipe=recipe)
        return shopping_list if created else None

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, id=None):
        recipe = self.get_object()
        if request.method == 'POST':
            favorite = self.create_favorite(request.user, recipe)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            favorite = Favorite.objects.get(user=request.user, recipe_id=id)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_list(self, request, id=None):
        recipe = self.get_object()
        if request.method == 'POST':
            shopping_list = self.create_shopping_list(request.user, recipe)
            if shopping_list:
                serializer = ShoppingListSerializer(shopping_list)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            shopping_list = ShoppingList.objects.get(
                user=request.user, recipe_id=id)
            shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_list(self, request):
        user = request.user
        output = self.create_shopping_list_file(user)
        response = FileResponse(output, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;filename="{file}.txt"')
        return response
