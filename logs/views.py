# Django imports
from django.shortcuts import get_object_or_404

# DRF imports
from rest_framework import status
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

# app imports
import logs.models as models
import logs.serializers as serializers
import manager.models as manager_models
import authentication.models as auth_models
import authentication.permissions as permissions


class ListLogsView(GenericAPIView, ListModelMixin, RetrieveModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsCompanyManager]
    serializer_class = serializers.LogSerializer
    queryset = models.Log.objects.all()

    def get(self, request, *args, **kwargs):
        if "id" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        manager = get_object_or_404(
            auth_models.AppUser, user=self.request.user)
        company = manager_models.Company.objects.get(manager=manager)
        return models.Log.objects.filter(app_user__company=company)