# Python imports
from datetime import datetime

# Django imports
from django.http import QueryDict
from django.db.models import Q, F
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
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin

# Module imports
import manager.utilities as utils
import document.models as doc_models
import shipment.models as ship_models
import manager.serializers as serializers
import authentication.models as auth_models
import document.serializers as doc_serializers
import shipment.serializers as ship_serializers
import authentication.permissions as permissions
import notifications.models as notif_models
import notifications.serializers as notif_serializers

# ThirdParty imports
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)

from freightmonster.thread import ThreadWithReturnValue

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
        created_by_company, customer_company, shipper_company, consignee_company, dispatcher_company, carrier_company = utils.get_parties_companies(
            instance)

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
    pagination_class = PageNumberPagination

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
            paginator = self.pagination_class()
            paginated_loads = paginator.paginate_queryset(
                queryset.order_by("-id"), request)
            serializer = self.get_serializer(paginated_loads, many=True)
            return paginator.get_paginated_response(serializer.data)

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
        contacts = serializers.ManagerContactListSerializer(
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

        company_contacts = auth_models.AppUser.objects.filter(
            id__in=distinct).order_by("-id")

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


class ListEmployeesShipmentsView(GenericAPIView, ListModelMixin, RetrieveModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = ship_serializers.ShipmentSerializer
    queryset = ship_models.Shipment.objects.all()
    pagination_class = PageNumberPagination
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        if self.kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

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

        shipments = (
            ship_models.Shipment.objects.filter(
                Q(id__in=shipments_from_admins) | Q(
                    created_by__in=company_employees)
            )
            .distinct()
            .order_by("-id")
        )
        queryset = queryset.filter(shipment__in=shipments)
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
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        load = get_object_or_404(ship_models.Load, id=self.kwargs["id"])
        company = auth_models.Company.objects.get(
            manager=auth_models.AppUser.objects.get(user=request.user)
        )
        created_by_company, customer_company, shipper_company, consignee_company, dispatcher_company, carrier_company = utils.get_parties_companies(
            load)
        if (
                created_by_company == company
                or customer_company == company
                or shipper_company == company
                or consignee_company == company
                or dispatcher_company == company
                or carrier_company == company
        ):
            queryset = self._handle_offers_filters(
                load, company, dispatcher_company, customer_company, carrier_company)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return exceptions.PermissionDenied(detail="You don't have access to view this load's information")

    def _handle_offers_filters(self, load: ship_models.Load, company, dispatcher_company, customer_company,
                               carrier_company):
        queryset = self.queryset
        queryset = queryset.filter(load=load)
        queryset = queryset.exclude(status="Rejected").order_by("id")
        # 2 main cases: Dispatcher (shows 2 offers), else: 3 cases: customer and carrier (show 2 offers), customer (shows 1 offer), carrier (shows 1 offer)
        if dispatcher_company == company:
            queryset = queryset.filter(
                party_1=load.dispatcher)  # Returns 2 offers
        else:
            if customer_company == company and carrier_company == company:
                queryset = queryset.filter(
                    Q(party_2=load.customer.app_user) | Q(party_2=load.carrier.app_user))
            elif customer_company == company:
                queryset = queryset.filter(party_2=load.customer.app_user)
            elif carrier_company == company:
                queryset = queryset.filter(party_2=load.carrier.app_user)
            else:
                queryset = queryset.none()
        return queryset


class ValidateEmployeeFinalAgreementView(GenericAPIView):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    queryset = doc_models.FinalAgreement.objects.all()

    def get(self, request, *args, **kwargs):
        if "load" not in request.query_params:
            raise exceptions.ParseError(detail="Please provide Load id")
        load = get_object_or_404(
            ship_models.Load, id=request.query_params.get("load"))
        company = auth_models.Company.objects.get(
            manager=auth_models.AppUser.objects.get(user=request.user)
        )
        created_by_company, customer_company, shipper_company, consignee_company, dispatcher_company, carrier_company = utils.get_parties_companies(
            load)
        if (
                created_by_company == company
                or customer_company == company
                or shipper_company == company
                or consignee_company == company
                or dispatcher_company == company
                or carrier_company == company
        ):
            data = {}
            final_agreement = get_object_or_404(
                doc_models.FinalAgreement, load_id=load.id)
            if dispatcher_company == company:
                data["did_customer_agree"] = final_agreement.did_customer_agree
                data["did_carrier_agree"] = final_agreement.did_carrier_agree
            elif carrier_company == company:
                data["did_carrier_agree"] = final_agreement.did_carrier_agree
            elif customer_company == company:
                data["did_customer_agree"] = final_agreement.did_customer_agree

            return Response(data=data, status=status.HTTP_200_OK)

        return exceptions.PermissionDenied(detail="You don't have access to view this load's information")


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


class ListEmpoloyeeNotificationsView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = notif_serializers.ManagerNotificationSerializer
    queryset = notif_models.Notification.objects.all()
    pagination_class = PageNumberPagination

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

        read_or_unread = self.request.query_params.get("seen", None)
        if read_or_unread is None:
            return self.queryset.none()
        elif read_or_unread == "read":
            return self.queryset.filter(user__in=company_employees, manager_seen=True).order_by("-id")
        elif read_or_unread == "unread":
            return self.queryset.filter(user__in=company_employees, manager_seen=False).order_by("-id")


class ManagerUpdateNotificationView(GenericAPIView, UpdateModelMixin):
    permission_classes = (IsAuthenticated, permissions.IsCompanyManager)
    serializer_class = notif_serializers.ManagerNotificationSerializer
    queryset = notif_models.Notification.objects.all()
    lookup_field = "id"

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        app_user = get_object_or_404(auth_models.AppUser, user=request.user)
        company = auth_models.Company.objects.get(manager=app_user)
        company_employees = auth_models.CompanyEmployee.objects.filter(
            company=company
        ).values_list("app_user", flat=True)
        if instance.user.id not in company_employees:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["manager_seen"] = request.data["seen"]
        del request.data["seen"]

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


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
        delivered_loads = filter_query.filter(status="Delivered")
        result = dict()

        dashboard_card_thread = ThreadWithReturnValue(
            target=utils.create_dashboard_cards,
            args=(filter_query, delivered_loads,)
        )
        dashboard_card_thread.start()

        dashboard_chart_thread = ThreadWithReturnValue(
            target=utils.create_dashboard_chart,
            args=(filter_query,)
        )
        dashboard_chart_thread.start()

        dashboard_load_types_thread = ThreadWithReturnValue(
            target=utils.create_dashboard_load_types,
            args=(filter_query,)
        )
        dashboard_load_types_thread.start()

        dashboard_offers_info_thread = ThreadWithReturnValue(
            target=utils.create_dashboard_offers_info,
            args=(delivered_loads,)
        )
        dashboard_offers_info_thread.start()

        dashboard_equipments_thread = ThreadWithReturnValue(
            target=utils.create_dashboard_equipment,
            args=(filter_query,)
        )
        dashboard_equipments_thread.start()

        dashboard_top_employees_thread = ThreadWithReturnValue(
            target=utils.create_dashboard_top_employees,
            args=(delivered_loads,)
        )
        dashboard_top_employees_thread.start()

        dashboard_delivery_performance = ThreadWithReturnValue(
            target=utils.get_dashboard_delivery_performance,
            args=(delivered_loads,)
        )
        dashboard_delivery_performance.start()

        result["cards"] = dashboard_card_thread.join()
        result["chart"] = dashboard_chart_thread.join()
        result["load_types"] = dashboard_load_types_thread.join()
        dashboard_offers_info_result = dashboard_offers_info_thread.join()
        result["carrier_offers"] = dashboard_offers_info_result["carrier_offers"]
        result["carriers_chart"] = dashboard_offers_info_result["carriers_chart"]
        result["customer_offers"] = dashboard_offers_info_result["customer_offers"]
        result["customers_chart"] = dashboard_offers_info_result["customers_chart"]
        result["total_paid"] = dashboard_offers_info_result["total_paid"]
        result["total_received"] = dashboard_offers_info_result["total_received"]
        result["revenue"] = dashboard_offers_info_result["total_received"]
        result["profit_summary_chart"] = dashboard_offers_info_result["profit_summary_chart"]
        result["equipments"] = dashboard_equipments_thread.join()
        result["top_employees"] = dashboard_top_employees_thread.join()
        result["delivery_performance"] = dashboard_delivery_performance.join()

        return Response(data=result, status=status.HTTP_200_OK)
