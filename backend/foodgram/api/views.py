from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from .permissions import IsAdminOrReadOnly, AuthorModeratorAdminOrReadOnly
from .serializers import (UsersSerializer, SubscribeSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          FavoriteSerializer, RecipeListSerializer)

from users.models import Subscriber
from rest_framework.permissions import IsAuthenticated
from recipes.models import (Tag, Ingredient,
                            Recipe, IngredientRecipe,
                            Favorite, ShoppingList)

User = get_user_model()


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='subscribe',
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user

        if not request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscriber.objects.bulk_create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not request.method == 'DELETE':
            get_object_or_404(
                Subscriber, user=user, author=author
            ).delete()
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
    permission_classes = (AuthorModeratorAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('is_favorited', 'author', 'tags', 'is_in_shopping_cart')
    paginator_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, id=None):
        recipe = self.get_object()
        if request.method == 'POST':
            favorite = Favorite.objects.create(user=request.user,
                                               recipe=recipe)
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
            shopping_list, created = ShoppingList.objects.get_or_create(
                user=request.user, recipe=recipe)
            if created:
                serializer = ShoppingListSerializer(shopping_list)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            shopping_list = ShoppingList.objects.get(user=request.user,
                                                     recipe_id=id)
            shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def add_to_shopping_list(self, request, id=None):
        recipe = self.get_object()
        shopping_list, created = ShoppingList.objects.get_or_create(
            user=request.user,
            recipe=recipe)
        if created:
            serializer = ShoppingListSerializer(shopping_list)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'],
            permission_classes=[IsAuthenticated])
    def remove_from_shopping_list(self, request, id=None):
        recipe = self.get_object()
        shopping_list = ShoppingList.objects.get(user=request.user,
                                                 recipe=recipe)
        shopping_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_list(self, request):
        user = request.user
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
        response = Response(output, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment;filename="{file}.txt"')
        return response
