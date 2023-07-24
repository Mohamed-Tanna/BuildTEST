# Module imports
import authentication.permissions as permissions
import notifications.serializers as serializers
import notifications.models as models
import authentication.models as auth_models
# Django imports
from django.shortcuts import get_object_or_404
# DRF imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin

class NotificationSettingView(GenericAPIView, UpdateModelMixin, RetrieveModelMixin):
    permission_classes = (IsAuthenticated, permissions.IsAppUser)
    serializer_class = serializers.NotificationSettingSerializer
    queryset = models.NotificationSetting.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        app_user = get_object_or_404(auth_models.AppUser, user=request.user)
        try:
            instance = models.NotificationSetting.objects.get(user=app_user)
        except (BaseException):
            return Response({"details": "NotificationSetting not found for this user."}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.NotificationSettingSerializer(instance).data
        return Response(serializer)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        app_user = get_object_or_404(auth_models.AppUser, user=request.user)
        if instance.user != app_user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
