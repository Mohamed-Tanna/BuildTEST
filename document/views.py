# python imports
import uuid

# DRF imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

# Django import
from django.utils import timezone
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404

# third party imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# module imports
import document.models as models
import shipment.models as ship_models
import shipment.utilities as ship_utils
import document.serializers as serializers
import authentication.permissions as permissions

NOT_AUTH_MSG = "You are not authorized to view this document."
SHIPMENT_PARTY = "shipment party"
LOAD_REQUIRED_MSG = "load is required."


class FileUploadView(GenericAPIView, ListModelMixin):
    permission_classes = [
        IsAuthenticated,
        permissions.HasRole,
    ]
    queryset = models.UploadedFile.objects.all()

    @swagger_auto_schema(
        operation_description="Get all files related to a load.",
        responses={
            200: serializers.RetrieveFileSerializer,
            400: "Bad request.",
            401: "Unauthorized.",
            403: "Forbidden.",
            404: "Not found.",
            500: "Internal server error.",
        },
    )
    def get(self, request, *args, **kwargs):
        """Get all files related to a load."""
        load_id = request.query_params.get("load")
        if load_id:
            return self.list(request, *args, **kwargs)
        else:
            return Response(
                [{"details": LOAD_REQUIRED_MSG}], status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Upload a file to a load.",
        request_body=serializers.UploadFileSerializer,
        responses={
            200: serializers.UploadFileSerializer,
            400: "Bad request.",
            401: "Unauthorized.",
            403: "Forbidden.",
            404: "Not found.",
            500: "Internal server error.",
        },
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
                queryset = models.UploadedFile.objects.filter(load=load)
            except ship_models.Load.DoesNotExist:
                queryset = models.UploadedFile.objects.none()
        else:
            queryset = []
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.RetrieveFileSerializer
        elif self.request.method == "POST":
            return serializers.UploadFileSerializer


class BillingDocumentsView(APIView):
    permission_classes = [IsAuthenticated, permissions.HasRole]

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
            except (BaseException) as e:
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
                serializers.CustomerFinalAgreementSerializer(final_agreement).data
            )

        return Response(serializers.BOLSerializer(final_agreement).data)


class ValidateFinalAgreementView(APIView):
    permission_classes = [IsAuthenticated, permissions.HasRole]

    @swagger_auto_schema(
        operation_description="Validate a final agreement.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "load": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={
            200: "OK.",
            400: "Bad request.",
            401: "Unauthorized.",
            403: "Forbidden.",
            404: "Not found.",
            500: "Internal server error.",
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

    @swagger_auto_schema(
        operation_description="Validate a final agreement.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "load": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={
            200: "OK.",
            400: "Bad request.",
            401: "Unauthorized.",
            403: "Forbidden.",
            404: "Not found.",
            500: "Internal server error.",
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
                customer = ship_utils.get_shipment_party_by_username(
                    request.user.username
                )
                if customer != load.customer:
                    return Response(
                        [{"details": NOT_AUTH_MSG}],
                        status=status.HTTP_403_FORBIDDEN,
                    )

                final_agreement.did_customer_agree = True
                final_agreement.customer_uuid = uuid.uuid4()
                final_agreement.save()
                data = serializers.CustomerFinalAgreementSerializer(
                    final_agreement
                ).data

            elif app_user.selected_role == "carrier":
                carrier = ship_utils.get_carrier_by_username(request.user.username)
                if carrier != load.carrier:
                    return Response(
                        [
                            {
                                "details": "You are not authorized to validate this document."
                            }
                        ],
                        status=status.HTTP_403_FORBIDDEN,
                    )

                final_agreement.did_carrier_agree = True
                final_agreement.carrier_uuid = uuid.uuid4()
                final_agreement.save()
                data = serializers.CarrierFinalAgreementSerializer(final_agreement).data

            else:
                return Response(
                    [{"details": "You are not authorized to validate this document."}],
                    status=status.HTTP_403_FORBIDDEN,
                )

            if final_agreement.did_carrier_agree and final_agreement.did_customer_agree:
                final_agreement.verified_at = timezone.now()
                final_agreement.save()

            return Response(status=status.HTTP_200_OK, data=data)

        except (BaseException) as e:
            print(f"Unexpected {e=}, {type(e)=}")
            return Response(
                [{"details": "FinAg-Val"}], status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
