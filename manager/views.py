# Django imports
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# DRF imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
import rest_framework.exceptions as exceptions
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

# Module imports
import manager.utilities as utils
import document.models as doc_models
import shipment.models as ship_models
import shipment.utilities as ship_utils
import manager.serializers as serializers
import authentication.models as auth_models
import document.serializers as doc_serializers
import shipment.serializers as ship_serializers
import authentication.permissions as permissions

# ThirdParty imports
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)


NOT_AUTH_MSG = "You are not authorized to view this document."
ERR_FIRST_PART = "should either include a `queryset` attribute,"
ERR_SECOND_PART = "or override the `get_queryset()` method."
NOT_AUTH_SHIPMENT = "You don't have access to view this shipment's information"


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

        manager = auth_models.AppUser.objects.get(user=self.request.user)
        try:
            company = auth_models.Company.objects.get(manager=manager)
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
            manager=auth_models.AppUser.objects.get(user=self.request.user)
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

        shipment_creator = instance.shipment.created_by
        try:
            shipment_creator_company = auth_models.CompanyEmployee.objects.get(
                app_user=shipment_creator
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            shipment_creator_company = None

        shipment_admins = ship_models.ShipmentAdmin.objects.filter(
            shipment=instance.shipment).values_list("admin", flat=True)
        shipment_admins_companies = auth_models.CompanyEmployee.objects.filter(
            app_user__in=shipment_admins).values_list("company", flat=True)

        if (
            created_by_company == company
            or customer_company == company
            or shipper_company == company
            or consignee_company == company
            or dispatcher_company == company
            or carrier_company == company
            or shipment_creator_company == company
            or company.id in shipment_admins_companies
        ):
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return exceptions.PermissionDenied(detail="You don't have access to view this load's information")


class ListEmployeesContactsView(GenericAPIView, ListModelMixin):
    """
    View for listing admin's company contacts
    """

    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = serializers.ManagerContactListSerializer
    queryset = ship_models.Contact.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        assert queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        company_manager = auth_models.AppUser.objects.get(
            user=self.request.user)

        try:
            company = auth_models.Company.objects.get(manager=company_manager)
        except auth_models.Company.DoesNotExist:
            return queryset.none()

        company_employees = auth_models.CompanyEmployee.objects.filter(
            company=company
        ).values_list("app_user", flat=True)
        origins = auth_models.AppUser.objects.filter(
            id__in=company_employees
        ).values_list("user", flat=True)
        origins = User.objects.filter(id__in=origins)
        company_contacts = (
            queryset.filter(Q(origin__in=origins)).distinct().order_by("-id")
        )

        distinct = set()
        for contact in company_contacts:
            distinct.add(contact.contact.id)

        company_contacts = auth_models.AppUser.objects.filter(id__in=distinct)

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
        company_manager = auth_models.AppUser.objects.get(
            user=self.request.user)

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


class ListEmployeesShipmentsView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.ShipmentSerializer
    queryset = ship_models.Shipment.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        assert queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        company_manager = auth_models.AppUser.objects.get(
            user=self.request.user)

        try:
            company = auth_models.Company.objects.get(manager=company_manager)
        except auth_models.Company.DoesNotExist:
            return queryset.none()

        company_employees = auth_models.CompanyEmployee.objects.filter(
            company=company
        ).values_list("app_user", flat=True)

        shipments_from_admins = ship_models.ShipmentAdmin.objects.filter(
            app_user__in=company_employees
        ).values_list("shipment", flat=True)

        queryset = (
            ship_models.Shipment.objects.filter(
                Q(id__in=shipments_from_admins) | Q(
                    created_by__in=company_employees)
            )
            .distinct()
            .order_by("-id")
        )

        return queryset


class RetrieveEmployeeShipmentView(GenericAPIView, RetrieveModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.LoadListSerializer
    queryset = ship_models.Load.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(
            ship_models.Shipment, id=self.kwargs["id"])
        try:
            company = auth_models.Company.objects.get(
                manager=auth_models.AppUser.objects.get(user=self.request.user)
            )
        except auth_models.Company.DoesNotExist:
            return exceptions.PermissionDenied(detail=NOT_AUTH_SHIPMENT)

        try:
            owner_company = auth_models.CompanyEmployee.objects.get(
                app_user=instance.owner).company
        except auth_models.CompanyEmployee.DoesNotExist:
            owner_company = None

        shipment_admins = ship_models.ShipmentAdmin.objects.filter(
            shipment=instance).values_list("app_user", flat=True)
        shipment_admins_companies = auth_models.CompanyEmployee.objects.filter(
            app_user__in=shipment_admins).values_list("company", flat=True)

        if owner_company == company or company.id in shipment_admins_companies:
            queryset = ship_models.Load.objects.filter(shipment=instance)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return exceptions.PermissionDenied(detail=NOT_AUTH_SHIPMENT)


class EmployeeBillingDocumentsView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]

    @extend_schema(
        description="Get all billing documents related to a load for company manager.",
        parameters=[
            OpenApiParameter(
                name="load",
                description="Filter billing documents by load.",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
        responses={
            status.HTTP_200_OK: doc_serializers.DispatcherFinalAgreementSerializer},
    )
    def get(self, request, *args, **kwargs):
        """Get all billing documents related to a load for company manager."""
        load_id = request.query_params.get("load")
        if load_id:
            load, company_employees = utils.check_manager_can_view_load(
                load_id, request.user)
            final_agreement = get_object_or_404(doc_models.FinalAgreement,
                                                load_id=load_id)
            return self._handle_agreement(request, load, final_agreement, company_employees)

    def _handle_agreement(self, request, load, final_agreement, company_employees):

        if ((load.dispatcher.app_user.id in company_employees)
                    or (load.customer.app_user.id in company_employees
                        and load.carrier.app_user.id in company_employees)
                ):
            return Response(
                status=status.HTTP_200_OK,
                data=doc_serializers.DispatcherFinalAgreementSerializer(
                    final_agreement).data
            )
        if load.customer.app_user.id in company_employees:
            return Response(
                status=status.HTTP_200_OK,
                data=doc_serializers.CustomerFinalAgreementSerializer(
                    final_agreement).data
            )
        if load.carrier.app_user.id in company_employees:
            return Response(
                status=status.HTTP_200_OK,
                data=doc_serializers.CarrierFinalAgreementSerializer(
                    final_agreement).data
            )
        if load.shipper.app_user.id in company_employees or load.consignee.app_user.id in company_employees:
            return Response(
                status=status.HTTP_200_OK,
                data=doc_serializers.BOLSerializer(
                    final_agreement).data
            )
        raise exceptions.PermissionDenied(detail=NOT_AUTH_MSG)


class EmployeeFileUploadedView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = doc_serializers.RetrieveFileSerializer
    queryset = doc_models.UploadedFile.objects.all()

    @extend_schema(
        description="Get all files related to a load.",
        parameters=[
            OpenApiParameter(
                name="load",
                description="Filter files by load.",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
        responses={status.HTTP_200_OK: doc_serializers.RetrieveFileSerializer},
    )
    def get(self, request, *args, **kwargs):
        """Get all uploaded documents related to a load for company manager."""
        load_id = request.query_params.get("load")
        if load_id:
            return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        assert queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )
        load_id = self.request.query_params.get("load")
        utils.check_manager_can_view_load(load_id, self.request.user)
        queryset = queryset.filter(load=load_id)
        return queryset
