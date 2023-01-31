from rest_framework.permissions import BasePermission


class OrderPermissions(BasePermission):

    def has_permission(self, request, view):

        groups = request.user.groups.all()
        if groups.filter(name='Manager').exists() or request.user.is_superuser:
            user = 'manager'
        elif groups.filter(name='Delivery Crew').exists():
            user = 'delivery'
        else:
            user = 'customer'

        match user, view.action:
            case 'customer', 'list' | 'retrieve' | 'create':
                return True
            case 'delivery', 'list' | 'partial_update':
                return True
            case 'manager', 'list' | 'partial_update' | 'update' | 'destroy':
                return True
            case _:
                return False


class IsManager(BasePermission):
    """
    Allows access only to manager users.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.groups.filter(name='Manager').exists() or request.user.is_superuser))


class IsCustomer(BasePermission):
    """
    Allows access only to customer users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.count() == 0)
