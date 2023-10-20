# python imports
import uuid

# DRF imports
from rest_framework import status
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

# Django import
from django.db.models import Q
from django.utils import timezone
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404

# module imports
import document.models as models
import shipment.models as ship_models
import shipment.utilities as ship_utils
import document.serializers as serializers
import authentication.permissions as permissions
from notifications.utilities import handle_notification

# ThirdParty imports
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)

NOT_AUTH_MSG = "You are not authorized to view this document."
SHIPMENT_PARTY = "shipment party"
LOAD_REQUIRED_MSG = "load is required."


class FileUploadView(GenericAPIView, ListModelMixin):
    permission_classes = [
        IsAuthenticated,
        permissions.HasRole,
    ]
    queryset = models.UploadedFile.objects.all()

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
        responses={status.HTTP_200_OK: serializers.RetrieveFileSerializer},
    )
    def get(self, request, *args, **kwargs):
        """Get all files related to a load."""
        load_id = request.query_params.get("load")
        if load_id:
            load = get_object_or_404(ship_models.Load, id=load_id)
            app_user = ship_utils.get_app_user_by_username(request.user.username)

            shipment = get_object_or_404(ship_models.Shipment, id=load.shipment)
            shipment_admins = ship_models.ShipmentParty.objects.filter(shipment=shipment.id).values_list("admin", flat=True)

            filters = Q(created_by=app_user.id)
            filters = ship_utils.apply_load_access_filters_for_user(filters, app_user)
            filters &= Q(load_id=load_id)
            queryset = queryset.filter(filters)

            if app_user.id not in shipment_admins and not self.queryset.exists():
                return Response(
                    {"details": "You do not have permission to view this load."},
                    status=status.HTTP_403_FORBIDDEN,
                )
                
            return self.list(request, *args, **kwargs)
        else:
            return Response(
                {"details": LOAD_REQUIRED_MSG}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        description="Upload a file.",
        request=inline_serializer(
            name="UploadFile",
            fields={
                "load": OpenApiTypes.STR,
                "uploaded_file": OpenApiTypes.BYTE,
                "uploaded_by": OpenApiTypes.STR,
                "name": OpenApiTypes.STR,
                "size": OpenApiTypes.FLOAT,
            },
        ),
        responses={status.HTTP_201_CREATED: serializers.UploadFileSerializer},
    )
    def post(self, request, *args, **kwargs):
        """Create a new file."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.create(request.data)

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )

        load_id = self.request.query_params.get("load")
        if load_id:
            try:
                load = ship_models.Load.objects.get(id=load_id)
                self.queryset = models.UploadedFile.objects.filter(load=load)
            except ship_models.Load.DoesNotExist:
                self.queryset = models.UploadedFile.objects.none()
        else:
            self.queryset = self.queryset.none()
        if isinstance(self.queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            self.queryset = self.queryset.all()
        return self.queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.RetrieveFileSerializer
        elif self.request.method == "POST":
            return serializers.UploadFileSerializer


class BillingDocumentsView(APIView):
    permission_classes = [IsAuthenticated, permissions.HasRole]

    @extend_schema(
        description="Get all billing documents related to a load.",
        parameters=[
            OpenApiParameter(
                name="load",
                description="Filter billing documents by load.",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
        responses={status.HTTP_200_OK: serializers.DispatcherFinalAgreementSerializer},
    )
    def get(self, request, *args, **kwargs):
        """Get all billing documents related to a load."""
        load_id = request.query_params.get("load")
        if load_id:
            try:
                load = ship_models.Load.objects.get(id=load_id)
                final_agreement = models.FinalAgreement.objects.get(load_id=load_id)
                app_user = ship_utils.get_app_user_by_username(request.user.username)

                if app_user.selected_role == "dispatcher":
                    return self._handle_dispatcher(request, load, final_agreement)

                elif app_user.selected_role == "carrier":
                    return self._handle_carrier(request, load, final_agreement)

                elif app_user.selected_role == SHIPMENT_PARTY:
                    return self._handle_shipment_party(request, load, final_agreement)

            except models.Load.DoesNotExist:
                return Response(
                    [{"details": "Load does not exist."}],
                    status=status.HTTP_404_NOT_FOUND,
                )
            except models.FinalAgreement.DoesNotExist:
                return Response(
                    [{"details": "Final agreement does not exist."}],
                    status=status.HTTP_404_NOT_FOUND,
                )
            except BaseException as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response(
                    [{"details": "FinAg"}], status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    def _handle_dispatcher(self, request, load, final_agreement):
        user = ship_utils.get_dispatcher_by_username(request.user.username)

        if user != load.dispatcher:
            return Response(
                [{"details": NOT_AUTH_MSG}],
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            serializers.DispatcherFinalAgreementSerializer(final_agreement).data
        )

    def _handle_carrier(self, request, load, final_agreement):
        user = ship_utils.get_carrier_by_username(request.user.username)

        if user != load.carrier:
            return Response(
                [{"details": NOT_AUTH_MSG}],
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            serializers.CarrierFinalAgreementSerializer(final_agreement).data
        )

    def _handle_shipment_party(self, request, load, final_agreement):
        user = ship_utils.get_shipment_party_by_username(request.user.username)

        if user != load.customer and user != load.shipper and user != load.consignee:
            return Response(
                [{"details": NOT_AUTH_MSG}],
                status=status.HTTP_403_FORBIDDEN,
            )
        elif user == load.customer:
            return Response(
                status=status.HTTP_200_OK,
                data=serializers.CustomerFinalAgreementSerializer(final_agreement).data,
            )

        return Response(
            status=status.HTTP_200_OK,
            data=serializers.BOLSerializer(final_agreement).data,
        )


class ValidateFinalAgreementView(APIView):
    permission_classes = [IsAuthenticated, permissions.HasRole]

    @extend_schema(
        description="Validate a final agreement.",
        request=inline_serializer(
            name="ValidateFinalAgreement",
            fields={
                "load": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="ValidateFinalAgreement",
                fields={
                    "did_customer_agree": OpenApiTypes.BOOL,
                    "did_carrier_agree": OpenApiTypes.BOOL,
                },
            ),
            status.HTTP_400_BAD_REQUEST: inline_serializer(
                name="ValidateFinalAgreement",
                fields={
                    "details": OpenApiTypes.STR,
                },
            ),
            status.HTTP_403_FORBIDDEN: inline_serializer(
                name="ValidateFinalAgreement",
                fields={
                    "details": OpenApiTypes.STR,
                },
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        """Get all billing documents related to a load."""

        if "load" not in request.query_params:
            return Response(
                [{"details": LOAD_REQUIRED_MSG}], status=status.HTTP_400_BAD_REQUEST
            )

        load_id = request.query_params.get("load")
        load = get_object_or_404(ship_models.Load, id=load_id)
        final_agreement = get_object_or_404(models.FinalAgreement, load_id=load_id)
        app_user = ship_utils.get_app_user_by_username(request.user.username)
        data = {}

        if app_user.selected_role == "dispatcher":
            dispatcher = ship_utils.get_dispatcher_by_username(request.user.username)
            if dispatcher != load.dispatcher:
                return Response(
                    [{"details": NOT_AUTH_MSG}],
                    status=status.HTTP_403_FORBIDDEN,
                )
            data["did_customer_agree"] = final_agreement.did_customer_agree
            data["did_carrier_agree"] = final_agreement.did_carrier_agree

        elif app_user.selected_role == "carrier":
            carrier = ship_utils.get_carrier_by_username(request.user.username)
            if carrier != load.carrier:
                return Response(
                    [{"details": NOT_AUTH_MSG}],
                    status=status.HTTP_403_FORBIDDEN,
                )
            data["did_carrier_agree"] = final_agreement.did_carrier_agree

        elif app_user.selected_role == SHIPMENT_PARTY:
            customer = ship_utils.get_shipment_party_by_username(request.user.username)
            if customer != load.customer:
                return Response(
                    [{"details": NOT_AUTH_MSG}],
                    status=status.HTTP_403_FORBIDDEN,
                )
            data["did_customer_agree"] = final_agreement.did_customer_agree

        return Response(status=status.HTTP_200_OK, data=data)

    @extend_schema(
        description="Validate a final agreement.",
        request=inline_serializer(
            name="ValidateFinalAgreement",
            fields={
                "load": OpenApiTypes.STR,
            },
        ),
        responses={
            status.HTTP_200_OK: serializers.CustomerFinalAgreementSerializer,
            status.HTTP_400_BAD_REQUEST: inline_serializer(
                name="ValidateFinalAgreement",
                fields={
                    "details": OpenApiTypes.STR,
                },
            ),
            status.HTTP_403_FORBIDDEN: inline_serializer(
                name="ValidateFinalAgreement",
                fields={
                    "details": OpenApiTypes.STR,
                },
            ),
        },
    )
    def put(self, request, *args, **kwargs):
        """Validate a final agreement."""
        if "load" not in request.data:
            return Response(
                [{"details": LOAD_REQUIRED_MSG}], status=status.HTTP_400_BAD_REQUEST
            )

        load = request.data["load"]
        load = get_object_or_404(ship_models.Load, id=load)
        final_agreement = get_object_or_404(models.FinalAgreement, load_id=load.id)
        app_user = ship_utils.get_app_user_by_username(request.user.username)

        try:
            if app_user.selected_role == SHIPMENT_PARTY:
                data = self._handle_customer_acceptance(request, load, final_agreement)

            elif app_user.selected_role == "carrier":
                data = self._handle_carrier_acceptance(request, load, final_agreement)

            else:
                return Response(
                    [{"details": "You are not authorized to validate this document."}],
                    status=status.HTTP_403_FORBIDDEN,
                )

            if final_agreement.did_carrier_agree and final_agreement.did_customer_agree:
                final_agreement.verified_at = timezone.now()
                final_agreement.save()

            return Response(status=status.HTTP_200_OK, data=data)

        except BaseException as e:
            print(f"Unexpected {e=}, {type(e)=}")
            raise e


    def _handle_customer_acceptance(self, request, load: ship_models.Load, final_agreement: models.FinalAgreement):
        customer = ship_utils.get_shipment_party_by_username(
                    request.user.username
        )
        if customer != load.customer:
            raise exceptions.PermissionDenied(
                NOT_AUTH_MSG
            )
        if final_agreement.did_customer_agree:
            raise exceptions.ParseError(
                "You have already validated this document."
            )
    
        final_agreement.did_customer_agree = True
        final_agreement.customer_uuid = uuid.uuid4()
        final_agreement.save()
        data = serializers.CustomerFinalAgreementSerializer(
            final_agreement
        ).data
        if load.dispatcher.app_user != customer.app_user:
            handle_notification(
                app_user=load.dispatcher.app_user,
                load=load,
                action="RC_approved",
                sender=customer.app_user,
            )

        return data    

    def _handle_carrier_acceptance(self, request, load: ship_models.Load, final_agreement: models.FinalAgreement):
        carrier = ship_utils.get_carrier_by_username(request.user.username)
        if carrier != load.carrier:
            raise exceptions.PermissionDenied(
                NOT_AUTH_MSG
            )

        if final_agreement.did_carrier_agree:
            raise exceptions.ParseError(
                "You have already validated this document."
            )
        
        final_agreement.did_carrier_agree = True
        final_agreement.carrier_uuid = uuid.uuid4()
        final_agreement.save()
        data = serializers.CarrierFinalAgreementSerializer(final_agreement).data
        if load.dispatcher.app_user != carrier.app_user:
            handle_notification(
                app_user=load.dispatcher.app_user,
                load=load,
                action="RC_approved",
                sender=carrier.app_user,
            )
        
        return data