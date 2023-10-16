# Django imports
from django.db.models import Q
from django.contrib.auth.models import User

# DRF imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

# Module imports
import shipment.models as ship_models
import authentication.models as auth_models
import shipment.serializers as ship_serializers
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
        queryset = (
            queryset.filter(
                Q(created_by__companyemployee__company=company)
                | Q(customer__app_user__companyemployee__company=company)
                | Q(shipper__app_user__companyemployee__company=company)
                | Q(consignee__app_user__companyemployee__company=company)
                | Q(dispatcher__app_user__companyemployee__company=company)
                | Q(carrier__app_user__companyemployee__company=company)
            )
            .distinct()
            .order_by("-id")
        )

        return queryset


class RetrieveEmployeeLoadView(GenericAPIView, RetrieveModelMixin):
    """
    View for retrieving employee load
    """

    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.LoadCreateRetrieveSerializer
    queryset = ship_models.Load.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        company = auth_models.Company.objects.get(
            admin=auth_models.AppUser.objects.get(user=self.request.user)
        )
        try:
            created_by_company = auth_models.CompanyEmployee.objects.get(
                app_user=instance.created_by
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            created_by_company = None

        try:
            customer_company = auth_models.CompanyEmployee.objects.get(
                app_user=instance.customer.app_user
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            customer_company = None

        try:
            shipper_company = auth_models.CompanyEmployee.objects.get(
                app_user=instance.shipper.app_user
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            shipper_company = None

        try:
            consignee_company = auth_models.CompanyEmployee.objects.get(
                app_user=instance.consignee.app_user
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            consignee_company = None

        try:
            dispatcher_company = auth_models.CompanyEmployee.objects.get(
                app_user=instance.dispatcher.app_user
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            dispatcher_company = None

        try:
            if instance.carrier:
                carrier_company = auth_models.CompanyEmployee.objects.get(
                    app_user=instance.carrier.app_user
                ).company
            else:
                carrier_company = None
        except auth_models.CompanyEmployee.DoesNotExist:
            carrier_company = None

        if (
            created_by_company == company
            or customer_company == company
            or shipper_company == company
            or consignee_company == company
            or dispatcher_company == company
            or carrier_company == company
        ):
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response(
            data={"details": "You don't have access to view this load's information"},
            status=status.HTTP_403_FORBIDDEN,
        )


class ListEmployeesContacsView(GenericAPIView, ListModelMixin):
    """
    View for listing admin's company contacts
    """

    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.ContactListSerializer
    queryset = ship_models.Contact.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        assert queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        company_manager = auth_models.AppUser.objects.get(user=self.request.user)

        try:
            company = auth_models.Company.objects.get(manager=company_manager)
        except auth_models.Company.DoesNotExist:
            return queryset.none()

        company_employees = auth_models.CompanyEmployee.objects.filter(
            company=company
        ).values_list("app_user", flat=True)
        print(company_employees)
        origins = auth_models.AppUser.objects.filter(
            id__in=company_employees
        ).values_list("user", flat=True)
        origins = User.objects.filter(id__in=origins)
        company_contacts = (
            queryset.filter(Q(origin__in=origins) | Q(contact__in=company_employees))
            .distinct()
            .order_by("-id")
        )
        return company_contacts


class ListEmployeesFacilitiesView(GenericAPIView, ListModelMixin):
    """
    View for listing all company employees facilities
    """

    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.FacilitySerializer
    queryset = ship_models.Facility.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        assert queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        company_manager = auth_models.AppUser.objects.get(user=self.request.user)

        try:
            company = auth_models.Company.objects.get(manager=company_manager)
        except auth_models.Company.DoesNotExist:
            return queryset.none()

        company_employees = auth_models.CompanyEmployee.objects.filter(
            company=company
        ).values_list("app_user", flat=True)
        owners = auth_models.AppUser.objects.filter(
            id__in=company_employees
        ).values_list("user", flat=True)
        owners = User.objects.filter(id__in=owners)
        facilities = (
            ship_models.Facility.objects.filter(owner__in=owners)
            .distinct()
            .order_by("-id")
        )

        return facilities
