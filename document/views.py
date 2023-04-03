# DRF imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

# Django import
from django.db.models.query import QuerySet

# third party imports
from drf_yasg.utils import swagger_auto_schema

# module imports
import document.models as models
import shipment.models as ship_models
import shipment.utilities as ship_utils
import document.serializers as serializers
import authentication.permissions as permissions


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
            return Response([{"details": "load is required."}], status=status.HTTP_400_BAD_REQUEST)


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
            "or override the `get_queryset()` method."
            % self.__class__.__name__
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


class BillingDocumnetsView(APIView):
    permission_classes = [IsAuthenticated, permissions.HasRole]
    
    def get(self, request, *args, **kwargs):
        """Get all billing documents related to a load."""
        load_id = request.query_params.get("load")
        if load_id:
            try:
                load = ship_models.Load.objects.get(id=load_id)
                final_agreement = models.FinalAgreement.objects.get(load_id=load_id)
                app_user = ship_utils.get_app_user_by_username(request.user.username)
                
                if app_user.user_type == "broker":
                    return self._handle_broker(request, load, final_agreement)
                    
                elif app_user.user_type == "carrier":
                    return self._handle_carrier(request, load, final_agreement)
                
                elif app_user.user_type == "shipment party":
                    return self._handle_shipment_party(request, load, final_agreement)
                
            except models.Load.DoesNotExist:
                return Response([{"details": "Load does not exist."}], status=status.HTTP_404_NOT_FOUND)
            except models.FinalAgreement.DoesNotExist:
                return Response([{"details": "Final agreement does not exist."}], status=status.HTTP_404_NOT_FOUND)
            except (BaseException) as e:
                print(f"Unexpected {e=}, {type(e)=}")
                return Response([{"details": "FinAg"}], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _handle_broker(self, request, load, final_agreement):
        user = ship_utils.get_broker_by_username(request.user.username)
        
        if user != load.broker:
            return Response([{"details": "You are not authorized to view this document."}], status=status.HTTP_403_FORBIDDEN)
            
        return Response(serializers.BrokerFinalAgreementSerializer(final_agreement).data)
    
    def _handle_carrier(self, request, load, final_agreement):
        user = ship_utils.get_carrier_by_username(request.user.username)
        
        if user != load.carrier:
            return Response([{"details": "You are not authorized to view this document."}], status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializers.CarrierFinalAgreementSerializer(final_agreement).data)
    
    def _handle_shipment_party(self, request, load, final_agreement):
        user = ship_utils.get_shipment_party_by_username(request.user.username)
        
        if user != load.customer and user != load.shipper and user != load.consignee:
            return Response([{"details": "You are not authorized to view this document."}], status=status.HTTP_403_FORBIDDEN)
        elif user == load.customer:
            return Response(serializers.CustomerFinalAgreementSerializer(final_agreement).data)
        
        return Response(serializers.BOLSerializer(final_agreement).data)