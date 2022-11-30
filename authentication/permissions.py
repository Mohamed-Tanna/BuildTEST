from rest_framework import permissions
from .models import *

class IsAppUser(permissions.BasePermission):

    message = "User profile incomplete, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        
        return AppUser.objects.filter(user=request.user).exists()


class IsBroker(permissions.BasePermission):

    message = "User is not a broker, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = AppUser.objects.get(user=request.user)
            return Broker.objects.filter(app_user=app_user).exists()
        except AppUser.DoesNotExist:
            return False


class IsCarrier(permissions.BasePermission):

    message = "User is not a carrier, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = AppUser.objects.get(user=request.user)
            return Carrier.objects.filter(app_user=app_user).exists()
        except AppUser.DoesNotExist:
            return False


class IsShipmentParty(permissions.BasePermission):

    message = "User is not a shipment party, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = AppUser.objects.get(user=request.user)
            return ShipmentParty.objects.filter(app_user=app_user).exists()
        except AppUser.DoesNotExist:
            return False