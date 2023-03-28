import authentication.models as auth_models
import shipment.models as ship_models
from rest_framework import status
from rest_framework.response import Response
import string, random


def get_shipment_party_by_username(username):
    try:
        user = auth_models.User.objects.get(username=username)
        user = auth_models.AppUser.objects.get(user=user.id)
        user = auth_models.ShipmentParty.objects.get(app_user=user.id)
        return user
    except (auth_models.User.DoesNotExist, auth_models.AppUser.DoesNotExist, auth_models.ShipmentParty.DoesNotExist):
        return Response(
            {"detail": ["shipper does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except (BaseException) as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return Response(
            {"detail": [f"{e.args[0]}"]},
            status=status.HTTP_400_BAD_REQUEST,
        )


def get_carrier_by_username(username):
    try:
        user = auth_models.User.objects.get(username=username)
        user = auth_models.AppUser.objects.get(user=user.id)
        user = auth_models.Carrier.objects.get(app_user=user.id)
        return user
    except (auth_models.User.DoesNotExist, auth_models.AppUser.DoesNotExist, auth_models.Carrier.DoesNotExist):
        return Response(
            {"detail": ["carrier does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except (BaseException) as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return Response(
            {"detail": [f"{e.args[0]}"]},
            status=status.HTTP_400_BAD_REQUEST,
        )


def get_broker_by_username(username):
    try:
        user = auth_models.User.objects.get(username=username)
        user = auth_models.AppUser.objects.get(user=user.id)
        user = auth_models.Broker.objects.get(app_user=user.id)
        return user
    except (auth_models.User.DoesNotExist, auth_models.AppUser.DoesNotExist, auth_models.Broker.DoesNotExist):
        return Response(
            {"detail": ["broker does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except (BaseException) as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return Response(
            {"detail": [f"{e.args[0]}"]},
            status=status.HTTP_400_BAD_REQUEST,
        )


def get_app_user_by_username(username):
    try:
        user = auth_models.User.objects.get(username=username)
        user = auth_models.AppUser.objects.get(user=user.id)
        return user
    except (auth_models.User.DoesNotExist, auth_models.AppUser.DoesNotExist):
        return Response(
            {"detail": ["broker does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except (BaseException) as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return Response(
            {"detail": [f"{e.args[0]}"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

def generate_load_name() -> string:
    name = "L-" + (
                "".join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(6)
                )
            )
    return name

def generate_shipment_name() -> string:
    name = "SH-" + (
                "".join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(5)
                )
            )
    return name

def get_company_by_role(app_user):
    try:
        company_employee = auth_models.CompanyEmployee.objects.get(app_user=app_user)
        company = auth_models.Company.objects.get(id=company_employee.company.id)
        return company
    except auth_models.CompanyEmployee.DoesNotExist:
        return Response(
            {"detail": ["user has no tax information"]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except (BaseException) as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return Response(
            {"detail": [f"{e.args[0]}"]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
def get_user_tax_by_role(app_user):
    try:
        user_tax = auth_models.UserTax.objects.get(app_user=app_user)
        return user_tax
    except auth_models.UserTax.DoesNotExist:
        return Response(
            {"detail": ["user has no tax information"]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except (BaseException) as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return Response(
            {"detail": [f"{e.args[0]}"]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
def get_user_tax_or_company(app_user):
    """Returns the company or user tax of the user"""
    company = get_company_by_role(app_user)
    user_tax = get_user_tax_by_role(app_user)

    if isinstance(company, Response) and isinstance(user_tax, Response):
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if isinstance(company, auth_models.Company):
        return company
    
    return user_tax
    
def get_parties_tax(customer_username, broker_username):
    customer_app_user = get_app_user_by_username(customer_username)
    broker_app_user = get_app_user_by_username(broker_username)
    if isinstance(customer_app_user, Response):
        return customer_app_user
    if isinstance(broker_app_user, Response):
        return broker_app_user
    customer_tax = get_user_tax_or_company(customer_app_user)
    broker_tax = get_user_tax_or_company(broker_app_user)
    if isinstance(customer_tax, Response):
        return Response({"details": "The customer does not have any tax information."} ,status=status.HTTP_400_BAD_REQUEST)
    if isinstance(broker_tax, Response):
        return Response({"details": "The broker does not have any tax information."} ,status=status.HTTP_400_BAD_REQUEST)
    
    return True

def extract_billing_info(billing_info, party):
    if isinstance(billing_info, auth_models.Company):
        billing_info = {
            "name": billing_info.name,
            "address": billing_info.address.building_number
            + " "
            + billing_info.address.street
            + " "
            + billing_info.address.city
            + " "
            + billing_info.address.state
            + " "
            + billing_info.address.zip_code,
            "phone_number": billing_info.phone_number,
        }
    if isinstance(billing_info, auth_models.UserTax):
        billing_info = {
            "name": party.app_user.user.first_name
            + " "
            + party.app_user.user.last_name,
            "address": billing_info.address.building_number
            + " "
            + billing_info.address.street
            + " "
            + billing_info.address.city
            + " "
            + billing_info.address.state
            + " "
            + billing_info.address.zip_code,
            "phone_number": party.app_user.phone_number,
        }
        
    return billing_info