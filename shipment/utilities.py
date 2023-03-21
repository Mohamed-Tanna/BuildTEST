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

def get_company_by_employee(employee):
    try:
        company_employee = auth_models.CompanyEmployee.objects.get(employee=employee.app_user)
        company = auth_models.Company.objects.get(id=company_employee.company.id)
        return company
    except auth_models.CompanyEmployee.DoesNotExist:
        return Response(
            {"detail": ["company employee does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )