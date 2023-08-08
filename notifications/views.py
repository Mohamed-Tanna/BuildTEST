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
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, ListModelMixin


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
            return Response(
                {"details": "NotificationSetting not found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = serializers.NotificationSettingSerializer(instance).data
        return Response(serializer)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        app_user = get_object_or_404(auth_models.AppUser, user=request.user)
        if instance.user != app_user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class NotificationView(GenericAPIView, ListModelMixin):
    permission_classes = (IsAuthenticated, permissions.IsAppUser)
    serializer_class = serializers.NotificationSerializer
    queryset = models.Notification.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )
        read_or_unread = self.request.query_params.get("seen", None)
        if read_or_unread is None:
            return self.queryset.none()
        elif read_or_unread == "read":
            app_user = auth_models.AppUser.objects.get(user=self.request.user)
            return self.queryset.filter(user=app_user, seen=True).order_by("-id")
        elif read_or_unread == "unread":
            app_user = auth_models.AppUser.objects.get(user=self.request.user)
            return self.queryset.filter(user=app_user, seen=False).order_by("-id")
        

class UpdateNotificationView(GenericAPIView, UpdateModelMixin):
    permission_classes = (IsAuthenticated, permissions.IsAppUser)
    serializer_class = serializers.NotificationSerializer
    queryset = models.Notification.objects.all()
    lookup_field = "id"

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        app_user = get_object_or_404(auth_models.AppUser, user=request.user)
        if notification.user != app_user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        notification.seen = True
        notification.save()

        return Response(status=status.HTTP_200_OK)