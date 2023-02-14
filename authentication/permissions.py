from rest_framework import permissions
import authentication.models as models


class IsAppUser(permissions.BasePermission):

    message = "User profile incomplete, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):

        return models.AppUser.objects.filter(user=request.user).exists()


class IsBroker(permissions.BasePermission):

    message = "User is not a broker, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)
            return models.Broker.objects.filter(app_user=app_user).exists()
        except models.AppUser.DoesNotExist:
            return False


class IsCarrier(permissions.BasePermission):

    message = "User is not a carrier, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)
            return models.Carrier.objects.filter(app_user=app_user).exists()
        except models.AppUser.DoesNotExist:
            return False


class IsShipmentParty(permissions.BasePermission):

    message = "User is not a shipment party, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)
            return models.ShipmentParty.objects.filter(app_user=app_user).exists()
        except models.AppUser.DoesNotExist:
            return False


class IsShipmentPartyOrBroker(permissions.BasePermission):

    message = "User is not a shipment party nor a broker, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)

            return (
                models.ShipmentParty.objects.filter(app_user=app_user).exists()
                or models.Broker.objects.filter(app_user=app_user).exists()
            )
        except models.AppUser.DoesNotExist:
            return False

class HasRole(permissions.BasePermission):

    message = "This user does not have a specified role; please complete your account and try again later."

    def has_permission(self, request, view):
        try:
             app_user = models.AppUser.objects.get(user=request.user)
             return (
                models.ShipmentParty.objects.filter(app_user=app_user).exists()
                or models.Broker.objects.filter(app_user=app_user).exists() or models.Carrier.objects.filter(app_user=app_user).exists()
            )
        except models.AppUser.DoesNotExist:
            return False