# Django imports
from django.db.models import Q
from django.http import QueryDict

# DRF imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated

# Module imports
import shipment.models as ship_models
import shipment.serializers as ship_serializers
import authentication.models as auth_models
import authentication.permissions as permissions

ERR_FIRST_PART = "should either include a `queryset` attribute,"
ERR_SECOND_PART = "or override the `get_queryset()` method."


class ListEmployeesLoadsView(GenericAPIView, ListModelMixin):
    """
    View for retrieving employees loads
    """

    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.LoadListSerializer
    queryset = ship_models.Load.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        assert queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )

        company_admin = auth_models.AppUser.objects.get(user=self.request.user)
        try:
            company = auth_models.Company.objects.get(admin=company_admin)
        except auth_models.Company.DoesNotExist:
            return queryset.none()
        queryset = queryset.filter(
            Q(created_by__companyemployee__company=company)
            | Q(customer__app_user__companyemployee__company=company)
            | Q(shipper__app_user__companyemployee__company=company)
            | Q(consignee__app_user__companyemployee__company=company)
            | Q(dispatcher__app_user__companyemployee__company=company)
            | Q(carrier__app_user__companyemployee__company=company)
        ).order_by("-id")

        return queryset


class RetrieveEmployeeLoadView(GenericAPIView, RetrieveModelMixin):
    """
    View for retrieving employee load
    """

    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.LoadListSerializer
    queryset = ship_models.Load.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        company = auth_models.Company.objects.get(
            admin=auth_models.AppUser.objects.get(user=self.request.user)
        )
        if (
            instance.created_by.companyemployee.company == company
            or instance.customer.app_user.companyemployee.company == company
            or instance.shipper.app_user.companyemployee.company == company
            or instance.consignee.app_user.companyemployee.company == company
            or instance.dispatcher.app_user.companyemployee.company == company
            or instance.carrier.app_user.companyemployee.company == company
        ):
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response(
            data={"details": "You don't have access to view this load's information"},
            status=status.HTTP_403_FORBIDDEN,
        )
