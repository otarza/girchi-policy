from rest_framework import viewsets

from .models import GroupOfTen, Membership
from .serializers import GroupOfTenSerializer, MembershipSerializer


class GroupOfTenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for GroupOfTen CRUD operations.
    To be implemented in GP-026.
    """

    queryset = GroupOfTen.objects.all()
    serializer_class = GroupOfTenSerializer


class MembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Membership CRUD operations.
    To be implemented in GP-026.
    """

    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
