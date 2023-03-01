from authentication.models import User, AppUser, ShipmentParty, Carrier, Broker
from rest_framework import status
from rest_framework.response import Response
import string, random


def get_shipment_party_by_username(username):
    try:
        user = User.objects.get(username=username)
        user = AppUser.objects.get(user=user.id)
        user = ShipmentParty.objects.get(app_user=user.id)
        return user
    except (User.DoesNotExist, AppUser.DoesNotExist, ShipmentParty.DoesNotExist):
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
        user = User.objects.get(username=username)
        user = AppUser.objects.get(user=user.id)
        user = Carrier.objects.get(app_user=user.id)
        return user
    except (User.DoesNotExist, AppUser.DoesNotExist, Carrier.DoesNotExist):
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
        user = User.objects.get(username=username)
        user = AppUser.objects.get(user=user.id)
        user = Broker.objects.get(app_user=user.id)
        return user
    except (User.DoesNotExist, AppUser.DoesNotExist, Broker.DoesNotExist):
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
        user = User.objects.get(username=username)
        user = AppUser.objects.get(user=user.id)
        return user
    except (User.DoesNotExist, AppUser.DoesNotExist):
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