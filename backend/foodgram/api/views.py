from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404

from .permissions import IsAdminOrReadOnly, AuthorModeratorAdminOrReadOnly
from .serializers import (UsersSerializer, SubscriptionSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          FavoriteSerializer)

from users.models import User, Subscriber
from rest_framework.permissions import AllowAny, IsAuthenticated
from recipes.models import (Tag, Ingredient,
                            Recipe, IngredientRecipe,
                            Favorite, ShoppingList)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    @action(detail=False,
            methods=['post'],
            permission_classes=[AllowAny])
    def register(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {'message': 'Пользователь успешно зарегистрировован'},
                status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(viewsets.ViewSet):
    '''Вьюсет для подписок/отписок'''
    @action(detail=True, methods=['get'])
    def subscriptions(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        subs = Subscriber.objects.filter(user=user)
        serializer = SubscriptionSerializer(subs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        author_id = request.data.get('author_id')
        if not author_id:
            return Response({'message': 'Не указан id автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        author = get_object_or_404(User, pk=author_id)
        user = get_object_or_404(User, pk=pk)
        if not Subscriber.objects.filter(user=user, author=author).exists():
            subscriptions = [Subscriber(user=user, author=author)]
            Subscriber.objects.bulk_create(subscriptions)
            return Response({'message': f'Подписан на {author.username}'},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'message': f'Уже подписан на {author.username}'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=request.data.get('author_id'))
        user = get_object_or_404(User, pk=pk)
        if Subscriber.objects.filter(user=user, author=author).exists():
            Subscriber.objects.filter(user=user, author=author).delete()
            return Response({'message': f'Отписан от {author.username}'})
        else:
            return Response({'message': f'Не подписан на  {author.username}'},
                            status=status.HTTP_404_NOT_FOUND)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ('id',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AuthorModeratorAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('is_favorited', 'author', 'tags', 'is_in_shopping_cart')
    paginator_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            favorite = Favorite.objects.create(user=request.user,
                                               recipe=recipe)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            favorite = Favorite.objects.get(user=request.user, recipe_id=pk)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_list(self, request, pk=None):
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
                                                     recipe_id=pk)
            shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def add_to_shopping_list(self, request, pk=None):
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
    def remove_from_shopping_list(self, request, pk=None):
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
            'attachment;filename="shopping_list.txt"')
        return response
