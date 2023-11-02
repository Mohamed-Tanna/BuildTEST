# Python imports
from datetime import datetime

# Django imports
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models import Avg, Sum, Count
from django.shortcuts import get_object_or_404

# DRF imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import rest_framework.exceptions as exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as drf_serializers
from rest_framework.pagination import PageNumberPagination
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
import authentication.serializers as auth_serializers

# ThirdParty imports
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    inline_serializer,

)


NOT_AUTH_MSG = "You are not authorized to view this document."
ERR_FIRST_PART = "should either include a `queryset` attribute,"
ERR_SECOND_PART = "or override the `get_queryset()` method."
NOT_AUTH_SHIPMENT = "You don't have access to view this shipment's information"
IN_TRANSIT = "In Transit"
SHIPMENT_PARTY = "shipment party"
AWAITING_DISPATCHER = "Awaiting Dispatcher"
AWAITING_CARRIER = "Awaiting Carrier"
READY_FOR_PICKUP = "Ready For Pickup"
ASSIGNING_CARRIER = "Assigning Carrier"
AWAITING_CUSTOMER = "Awaiting Customer"


class ListEmployeesLoadsView(GenericAPIView, ListModelMixin):
    """
    View for retrieving employees loads
    """

    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.LoadListSerializer
    queryset = ship_models.Load.objects.all()
    lookup_field = "id"
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        loads = self.get_queryset()
        if "search" in request.data:
            search = request.data["search"]
            loads = loads.filter(name__icontains=search)

        paginator = self.pagination_class()
        paginated_loads = paginator.paginate_queryset(
            loads.order_by("-id"), request)
        loads = ship_serializers.LoadListSerializer(
            paginated_loads, many=True).data

        return paginator.get_paginated_response(loads)

    def get_queryset(self):
        queryset = self.queryset
        assert queryset is not None, (
            f"'%s' {ERR_FIRST_PART}" f"{ERR_SECOND_PART}" % self.__class__.__name__
        )

        queryset = utils.check_manager_can_view_load_queryset(
            queryset=queryset, user=self.request.user
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


class FilterEmployeeLoadsView(GenericAPIView, ListModelMixin):
    """
    view for Listing loads inside a shipment
    """
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.LoadListSerializer
    queryset = ship_models.Load.objects.all()
    lookup_field = "shipment"

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        instance = get_object_or_404(
            ship_models.Shipment, id=self.request.data["shipment"])
        try:
            company = auth_models.Company.objects.get(
                manager=auth_models.AppUser.objects.get(user=self.request.user)
            )
        except auth_models.Company.DoesNotExist:
            return exceptions.PermissionDenied(detail=NOT_AUTH_SHIPMENT)

        try:
            owner_company = auth_models.CompanyEmployee.objects.get(
                app_user=instance.created_by).company
        except auth_models.CompanyEmployee.DoesNotExist:
            owner_company = None

        shipment_admins = ship_models.ShipmentAdmin.objects.filter(
            shipment=instance).values_list("admin", flat=True)
        shipment_admins_companies = auth_models.CompanyEmployee.objects.filter(
            app_user__in=shipment_admins).values_list("company", flat=True)

        if owner_company == company or company.id in shipment_admins_companies:
            queryset = ship_models.Load.objects.filter(shipment=instance)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return exceptions.PermissionDenied(detail=NOT_AUTH_SHIPMENT)


class ListEmployeesContactsView(GenericAPIView, ListModelMixin):
    """
    View for listing admin's company contacts
    """

    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = serializers.ManagerContactListSerializer
    queryset = ship_models.Contact.objects.all()
    lookup_field = "id"
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contacts = self.get_queryset()
        if "search" in request.data:
            search = request.data["search"]
            contacts = contacts.filter(user__username__icontains=search)

        paginator = self.pagination_class()
        paginated_contacts = paginator.paginate_queryset(
            contacts.order_by("-id"), request)
        contacts = auth_serializers.AppUserSerializer(
            paginated_contacts, many=True).data

        return paginator.get_paginated_response(contacts)

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
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        facilities = self.get_queryset()
        if "search" in request.data:
            search = request.data["search"]
            facilities = facilities.filter(
                Q(address__address__icontains=search)
                | Q(address__city__icontains=search)
                | Q(address__state__icontains=search)
                | Q(address__zip_code__icontains=search)
                | Q(building_name__icontains=search)
            )

        paginator = self.pagination_class()
        paginated_facilities = paginator.paginate_queryset(
            facilities.order_by("-id"), request)
        facilities = ship_serializers.FacilitySerializer(
            paginated_facilities, many=True).data

        return paginator.get_paginated_response(facilities)

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


class ListEmployeesShipmentsView(GenericAPIView, RetrieveModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.ShipmentSerializer
    queryset = ship_models.Shipment.objects.all()
    lookup_field = "id"
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        shipments = self.get_queryset()
        if "search" in request.data:
            search = request.data["search"]
            shipments = shipments.filter(name__icontains=search)

        paginator = self.pagination_class()
        paginated_shipments = paginator.paginate_queryset(
            shipments.order_by("-id"), request)
        shipments = ship_serializers.ShipmentSerializer(
            paginated_shipments, many=True).data

        return paginator.get_paginated_response(shipments)

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
            admin__in=company_employees
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


class ListEmployeesShipmentAdminsView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.ShipmentAdminSerializer
    queryset = ship_models.ShipmentAdmin.objects.all()

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
            admin__in=company_employees
        ).values_list("shipment", flat=True)

        queryset = (
            ship_models.Shipment.objects.filter(
                Q(id__in=shipments_from_admins) | Q(
                    created_by__in=company_employees)
            )
            .distinct()
            .order_by("-id")
        )
        if self.request.GET.get("id"):
            shipment_id = self.request.GET.get("id")
            queryset = queryset.filter(shipment=shipment_id)
        else:
            queryset = []

        return queryset


class RetrieveEmployeeOfferView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.OfferSerializer
    queryset = ship_models.Offer.objects.all()

    def get(self, request, *args, **kwargs):
        if self.kwargs:
            load = get_object_or_404(ship_models.Load, id=self.kwargs["id"])
            company = auth_models.Company.objects.get(
                manager=auth_models.AppUser.objects.get(user=self.request.user)
            )
            created_by_company, customer_company, shipper_company, consignee_company, dispatcher_company, carrier_company = self._get_parties_companies(load)
            if (
                created_by_company == company
                or customer_company == company
                or shipper_company == company
                or consignee_company == company
                or dispatcher_company == company
                or carrier_company == company
            ):

                queryset = self._handle_offers_filters(load, company, dispatcher_company, customer_company, carrier_company)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            return exceptions.PermissionDenied(detail="You don't have access to view this load's information")
        else:
            raise exceptions.ParseError(detail="Please provide Load id")

    def _handle_offers_filters(self, load: ship_models.Load, company, dispatcher_company, customer_company, carrier_company):
        queryset = self.queryset
        queryset = queryset.filter(load=load)
        queryset = queryset.exclude(status="Rejected").order_by("id")
        # 2 main cases: Dispatcher (shows 2 offers), else: 3 cases: customer and carrier (show 2 offers), customer (shows 1 offer), carrier (shows 1 offer)
        if dispatcher_company == company:
            queryset = queryset.filter(party_1=load.dispatcher) # Returns 2 offers
        else:
            if customer_company == company and carrier_company == company:
                queryset = queryset.filter(Q(party_2=load.customer.app_user) | Q(party_2=load.carrier.app_user))
            elif customer_company == company:
                queryset = queryset.filter(party_2=load.customer.app_user)
            elif carrier_company == company:
                queryset = queryset.filter(party_2=load.carrier.app_user)
            else:
                queryset = queryset.none()
        return queryset

    def _get_parties_companies(self, load):
        try:
            created_by_company = auth_models.CompanyEmployee.objects.get(
                app_user=load.created_by
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            created_by_company = None

        try:
            customer_company = auth_models.CompanyEmployee.objects.get(
                app_user=load.customer.app_user
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            customer_company = None

        try:
            shipper_company = auth_models.CompanyEmployee.objects.get(
                app_user=load.shipper.app_user
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            shipper_company = None

        try:
            consignee_company = auth_models.CompanyEmployee.objects.get(
                app_user=load.consignee.app_user
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            consignee_company = None

        try:
            dispatcher_company = auth_models.CompanyEmployee.objects.get(
                app_user=load.dispatcher.app_user
            ).company
        except auth_models.CompanyEmployee.DoesNotExist:
            dispatcher_company = None

        try:
            if load.carrier:
                carrier_company = auth_models.CompanyEmployee.objects.get(
                    app_user=load.carrier.app_user
                ).company
            else:
                carrier_company = None
        except auth_models.CompanyEmployee.DoesNotExist:
            carrier_company = None
        return created_by_company, customer_company, shipper_company, consignee_company, dispatcher_company, carrier_company

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


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]

    @extend_schema(
        responses={
            200: inline_serializer(
                name="Dashboard",
                fields={
                    "cards": inline_serializer(
                        name="Cards",
                        fields={
                            "total": drf_serializers.IntegerField(),
                            "pending": drf_serializers.IntegerField(),
                            "ready_for_pick_up": drf_serializers.IntegerField(),
                            "in_transit": drf_serializers.IntegerField(),
                            "delivered": drf_serializers.IntegerField(),
                            "canceled": drf_serializers.IntegerField(),
                            "loads": ship_serializers.LoadListSerializer(),
                        },
                    ),
                    "chart": inline_serializer(
                        name="Chart",
                        fields={
                            "0": inline_serializer(
                                name="Month",
                                fields={
                                    "name": drf_serializers.CharField(),
                                    "total": drf_serializers.IntegerField(),
                                    "pending": drf_serializers.IntegerField(),
                                    "ready_for_pick_up": drf_serializers.IntegerField(),
                                    "in_transit": drf_serializers.IntegerField(),
                                    "delivered": drf_serializers.IntegerField(),
                                    "canceled": drf_serializers.IntegerField(),
                                },
                            ),
                        },
                    ),
                },
            )
        },
    )
    def get(self, request, *args, **kwargs):
        """Get dashboard data for company manager."""
        filter_query = ship_models.Load.objects.all()
        filter_query = utils.check_manager_can_view_load_queryset(
            queryset=filter_query, user=self.request.user
        )
        if filter_query.exists() is False:
            raise exceptions.NotFound(detail="No loads found.")

        result = {}
        cards = {}
        cards["total"] = filter_query.count()
        cards["pending"] = filter_query.filter(
            status__in=[
                "Created",
                AWAITING_CUSTOMER,
                ASSIGNING_CARRIER,
                AWAITING_CARRIER,
                AWAITING_DISPATCHER,
            ]
        ).count()

        cards["ready_for_pick_up"] = filter_query.filter(
            status=READY_FOR_PICKUP).count()
        cards["in_transit"] = filter_query.filter(status=IN_TRANSIT).count()
        cards["delivered"] = filter_query.filter(status="Delivered").count()
        cards["canceled"] = filter_query.filter(status="Canceled").count()

        loads = filter_query.order_by("-id")[:3]

        loads = ship_serializers.LoadListSerializer(loads, many=True).data
        cards["loads"] = loads
        result["cards"] = cards
        result["chart"] = []

        year = datetime.now().year
        for i in range(1, 13):
            monthly_loads = filter_query.filter(
                created_at__month=i, created_at__year=year)
            obj = {}
            obj["name"] = datetime.strptime(str(i), "%m").strftime("%b")
            if monthly_loads.exists() is False:
                obj["total"] = 0
                obj["pending"] = 0
                obj["ready_for_pick_up"] = 0
                obj["in_transit"] = 0
                obj["delivered"] = 0
                obj["canceled"] = 0
                result["chart"].append(obj)
                continue
            obj["total"] = monthly_loads.count()
            obj["pending"] = monthly_loads.filter(
                status__in=[
                    "Created",
                    AWAITING_CUSTOMER,
                    ASSIGNING_CARRIER,
                    AWAITING_CARRIER,
                    AWAITING_DISPATCHER,
                ]
            ).count()

            obj["ready_for_pick_up"] = monthly_loads.filter(
                status=READY_FOR_PICKUP
            ).count()
            obj["in_transit"] = monthly_loads.filter(status=IN_TRANSIT).count()
            obj["delivered"] = monthly_loads.filter(status="Delivered").count()
            obj["canceled"] = monthly_loads.filter(status="Canceled").count()
            result["chart"].append(obj)

        # getting number of FTL,LTL, heavy haul loads
        ftl = filter_query.filter(load_type="FTL").count()
        ltl = filter_query.filter(load_type="LTL").count()
        # TODO: To be added to the model
        heavy_haul = filter_query.filter(load_type="HHL").count()

        result["load_types"] = {
            "ftl": ftl,
            "ltl": ltl,
            "HHL": heavy_haul,
        }

        # Get bar charts for cost of shipping to each carrier
        carrier_offers = ship_models.Offer.objects.filter(
            load__in=filter_query, status="Accepted", party_2__user_type__contains="carrier"
        )

        carriers = carrier_offers.values_list("party_2", flat=True).distinct()
        result["carrier_offers"] = {}

        for carrier in carriers:
            aggregates = carrier_offers.filter(party_2=carrier).aggregate(
                avg=Avg("current"), sum=Sum("current"))
            carrier = auth_models.AppUser.objects.get(id=carrier).user
            """  TODO: just to check if needed more stats
            carrier_obj = {}
            carrier_obj["name"] = carrier
            carrier_obj["number_of_loads"] = carrier_offers.filter(party_2=carrier).count()
            carrier_obj["average_cost"] = aggregates["avg"]
            carrier_obj["total_cost"] = aggregates["sum"]
            result["carrier_offers"].append(carrier_obj)
            result["carrier_offers"].append(carrier_obj)    
            """
            result["carrier_offers"][carrier.username] = aggregates["avg"]

        # Get top 5-10 equipments used with number of uses
        equipments = filter_query.values("equipment").annotate(
            equipment_count=Count("equipment")).order_by("-equipment_count")[:10]
        result["equipments"] = {}
        for equipment in equipments:
            result["equipments"][equipment["equipment"]
                                 ] = equipment["equipment_count"]

        return Response(data=result, status=status.HTTP_200_OK)
