from rest_framework import permissions
import authentication.models as models


class IsCloudFunction(permissions.BasePermission):
    message = "Can't access this"

    def has_permission(self, request, view):
        return request.user.email == "cloud-function-listen-to-stora@freightmonster-dev.iam.gserviceaccount.com"


class IsAppUser(permissions.BasePermission):
    message = "User profile incomplete, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        return models.AppUser.objects.filter(user=request.user).exists()


class IsDispatcher(permissions.BasePermission):
    message = "User is not a dispatcher, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)
            return models.Dispatcher.objects.filter(app_user=app_user).exists()
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


class IsShipmentPartyOrDispatcher(permissions.BasePermission):
    message = "User is not a shipment party nor a dispatcher, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)

            return (
                    models.ShipmentParty.objects.filter(app_user=app_user).exists()
                    or models.Dispatcher.objects.filter(app_user=app_user).exists()
            )
        except models.AppUser.DoesNotExist:
            return False


class IsShipmentPartyOrCarrier(permissions.BasePermission):
    message = "User is not a shipment party nor a carrier, fill out all of the profile's necessary information before trying again."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)

            return (
                    models.ShipmentParty.objects.filter(app_user=app_user).exists()
                    or models.Carrier.objects.filter(app_user=app_user).exists()
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
                    or models.Dispatcher.objects.filter(app_user=app_user).exists()
                    or models.Carrier.objects.filter(app_user=app_user).exists()
            )
        except models.AppUser.DoesNotExist:
            return False


class IsCompanyManager(permissions.BasePermission):
    message = "This user is not a company manager, if you believe this is an error, please contact support."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)
            return app_user.user_type == "manager"
        except models.AppUser.DoesNotExist:
            return False


class IsNotCompanyManager(permissions.BasePermission):
    message = "This user is a company manager, if you believe this is an error, please contact support."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)
            return app_user.user_type != "manager"
        except models.AppUser.DoesNotExist:
            return False


class HasRoleOrIsCompanyManager(permissions.BasePermission):
    def has_permission(self, request, view):
        has_role_permission = HasRole().has_permission(request, view)
        is_company_manager_permission = IsCompanyManager().has_permission(request, view)
        return has_role_permission or is_company_manager_permission


class IsSupport(permissions.BasePermission):
    message = "This user is not a support agent."

    def has_permission(self, request, view):
        try:
            app_user = models.AppUser.objects.get(user=request.user)
            return app_user.user_type == "support"
        except models.AppUser.DoesNotExist:
            return False
