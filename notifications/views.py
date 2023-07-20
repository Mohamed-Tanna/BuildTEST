# Module imports
import authentication.permissions as permissions
import notifications.serializers as serializers
import notifications.models as models
import authentication.models as auth_models
# DRF imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as drf_serializers
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin

class NotificationSettingView(GenericAPIView, UpdateModelMixin, RetrieveModelMixin):
    permission_classes = (IsAuthenticated, permissions.IsAppUser)
    serializer_class = serializers.NotificationSetting
    queryset = models.NotificationSetting.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        app_user = auth_models.AppUser.objects.get(id=request.user.id)
        instance = models.NotificationSetting.objects.get(user=app_user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        app_user = auth_models.AppUser.objects.get(id=request.user.id)
        if instance.user != app_user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
