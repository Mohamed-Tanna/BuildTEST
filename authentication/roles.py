from rolepermissions.roles import AbstractUserRole

class UserRole(AbstractUserRole):

    available_permissions = {}

class AppUserRole(AbstractUserRole):

    available_permissions = {}

class CarrierRole(AbstractUserRole):

    available_permissions = {}

class BrokerRole(AbstractUserRole):

    available_permissions = {}

class ShipmentPartyRole(AbstractUserRole):

    available_permissions = {}