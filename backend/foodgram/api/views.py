from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import (UsersSerializer, SubscriptionSerializer,
                          TagSerializer, IngredientSerializer, RecipeSerializer)

from users.models import User, Subscribed
from rest_framework.permissions import  AllowAny, IsAuthenticated
from recipes.models import Tag, Ingredient, Recipe
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    '''Вьюсет для автора , юзера , для подписок/отписок'''
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    #permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get', 'post'])
    def subscriptions(self, request, pk=None):
        user = self.get_object()
        subs = Subscribed.objects.filter(user=user)
        serializer = SubscriptionSerializer(subs,
                                            many=True,
                                            context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=request.data.get('author_id'))
        user = self.get_object()
        if not Subscribed.objects.filter(user=user, author=author).exists():
            Subscribed.objects.create(user=user, author=author)
            return Response({'message': f'Подписан на {author.username}'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': f'Уже подписался на {author.username}'})

    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=request.data.get('author_id'))
        user = self.get_object()
        if Subscribed.objects.filter(user=user, author=author).exists():
            Subscribed.objects.filter(user=user, author=author).delete()
            return Response({'message': f'Отписался {author.username}'})
        else:
            return Response({'message': f'Не подписан на  {author.username}'},
                            status=status.HTTP_404_NOT_FOUND)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)