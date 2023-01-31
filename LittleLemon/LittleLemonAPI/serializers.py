from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Category, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', ]


class MenuItemSerializer(serializers.ModelSerializer):
    category_title = serializers.StringRelatedField(read_only=True, source='category')

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_title', ]
        extra_kwargs = {
            'category': {
                'write_only': True
            }
        }


class GroupSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(source='id')
    username = serializers.CharField(read_only=True)


class CartSerializer(serializers.ModelSerializer):
    title = serializers.StringRelatedField(source='menuitem', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    quantity = serializers.IntegerField()
    unit_price = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'title', 'unit_price', 'quantity', 'price', ]

    def get_unit_price(self, product: Cart):
        return product.menuitem.price

    def get_price(self, product: Cart):
        return product.quantity * product.menuitem.price


class OrderItemsSerializer(serializers.ModelSerializer):
    title = serializers.StringRelatedField(source='menuitem', read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_kwargs = {
            'order': {
                'read_only': True
            },
        }


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(many=True)
    link = serializers.HyperlinkedIdentityField(view_name='order-detail')

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'total': {
                'read_only': True
            },
        }

    def create(self, validated_data):
        items = validated_data.pop('items')
        total = sum([item['price'] for item in items])

        order = Order.objects.create(total=total, **validated_data)

        for item in items:
            OrderItem.objects.create(order=order, **item)
        return order
