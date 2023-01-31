from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet, MenuItemViewSet, \
    ManagerGroupViewSet, DeliveryCrewGroupViewSet, \
    CartViewSet, OrderViewSet

ROUTERS_ARGS = [
    (r'categories', CategoryViewSet),
    (r'menu-items', MenuItemViewSet),
    (r'orders', OrderViewSet),
    (r'groups/manager/users', ManagerGroupViewSet),
    (r'groups/delivery-crew/users', DeliveryCrewGroupViewSet),
]

routers = [SimpleRouter(trailing_slash=False) for _ in ROUTERS_ARGS]

urlpatterns = [
    path('cart/menu-items', CartViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'clear'})),
]

for router, args in zip(routers, ROUTERS_ARGS):
    router.register(*args)
    urlpatterns += router.urls
