from authentication.models import *
from rest_framework import status
from rest_framework.response import Response


def get_shipment_party_by_username(username):
    try:
        user = User.objects.get(username=username)
        user = AppUser.objects.get(user=user.id)
        user = ShipmentParty.objects.get(app_user=user.id)
        return user
    except User.DoesNotExist or AppUser.DoesNotExist or ShipmentParty.DoesNotExist:
        return Response(
            {"detail": ["shipper does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except BaseException as e:
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
    except User.DoesNotExist or AppUser.DoesNotExist or Carrier.DoesNotExist:
        return Response(
            {"detail": ["carrier does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except BaseException as e:
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
    except User.DoesNotExist or AppUser.DoesNotExist or Broker.DoesNotExist:
        return Response(
            {"detail": ["broker does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except BaseException as e:
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
    except User.DoesNotExist or AppUser.DoesNotExist:
        return Response(
            {"detail": ["broker does not exist."]},
            status=status.HTTP_404_NOT_FOUND,
        )
    except BaseException as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return Response(
            {"detail": [f"{e.args[0]}"]},
            status=status.HTTP_400_BAD_REQUEST,
        )
