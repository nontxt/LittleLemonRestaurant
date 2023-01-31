from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .permissions import IsManager, IsCustomer, OrderPermissions
from .models import Category, MenuItem, Cart, Order
from .serializers import CategorySerializer, MenuItemSerializer, GroupSerializer, CartSerializer, OrderSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return [permission() for permission in self.permission_classes]


class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManager, ]
    search_fields = ['title', 'category__title', ]
    filterset_fields = ['title', 'price', 'featured']
    ordering = ['id', ]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []

        return [permission() for permission in self.permission_classes]


class ManagerGroupViewSet(ListModelMixin,
                          CreateModelMixin,
                          DestroyModelMixin,
                          GenericViewSet):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = GroupSerializer
    permission_classes = [IsManager, ]
    group = Group.objects.get(name='Manager')
    filter_backends = []
    ordering_fields = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer['user_id'].value
        user = get_object_or_404(User, id=user_id)
        user.groups.add(self.group)
        return Response({'message': 'User added to the Manager group.'}, status=HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('pk'))
        user.groups.remove(self.group)
        return Response({'message': 'User removed from the Manager group.'}, status=HTTP_200_OK)


class DeliveryCrewGroupViewSet(ListModelMixin,
                               CreateModelMixin,
                               DestroyModelMixin,
                               GenericViewSet):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = GroupSerializer
    permission_classes = [IsManager, ]
    group = Group.objects.get(name='Delivery Crew')
    filter_backends = []
    ordering_fields = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer['user_id'].value
        user = get_object_or_404(User, id=user_id)
        user.groups.add(self.group)
        return Response({'message': 'User added to the Delivery Crew group.'}, status=HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('pk'))
        user.groups.remove(self.group)
        return Response({'message': 'User removed from the Delivery Crew group.'}, status=HTTP_200_OK)


class CartViewSet(ListModelMixin,
                  CreateModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsCustomer, IsAuthenticated, ]
    filter_backends = []
    ordering_fields = []

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    def clear(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return Response({'message': 'Cart has been cleared.'}, status=HTTP_204_NO_CONTENT)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderPermissions]
    ordering = ['-id']
    search_fields = ['user', 'delivery_crew__username']

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.groups.filter(name='Manager').exists():
            return self.queryset.all()

        if user.groups.filter(name='Delivery Crew').exists():
            return self.queryset.filter(delivery_crew=user)

        return self.queryset.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        user = self.request.user
        user_group = list(user.groups.values_list('name', flat=True))

        if 'Manager' not in user_group:
            if len(request.data) > 1 or request.data.get('status') is None:
                raise PermissionDenied

        return super(OrderViewSet, self).partial_update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        cart = Cart.objects.filter(user=user)

        if len(cart) == 0:
            raise NotFound({'message': 'Your cart is empty.'})

        cart_serializer = CartSerializer(cart, many=True)
        data = {
            'user': user.id,
            'items': cart_serializer.data
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        cart.delete()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
