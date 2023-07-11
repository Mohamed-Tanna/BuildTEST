from rest_framework import status
import authentication.models as models
from google.cloud import secretmanager
import string, random, os, re, requests
from django.utils.html import strip_tags
from rest_framework.response import Response
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives


def create_address(created_by, address, city, state, country, zip_code):
    try:
        address = models.Address.objects.create(
            created_by=created_by,
            address=address,
            city=city,
            state=state,
            country=country,
            zip_code=zip_code,
        )
        address.save()
        return address

    except (BaseException) as e:
        print((f"Unexpected {e=}, {type(e)=}"))
        return False


def generate_company_identiefier():
    identiefier = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
    )
    return identiefier


def check_dot_number(dot_number):

    client = secretmanager.SecretManagerServiceClient()
    webkey = client.access_secret_version(
        request={
            "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('FMCSA_WEBKEY')}/versions/1"
        }
    )
    webkey = webkey.payload.data.decode("UTF-8")
    dot_pattern = re.compile(r"^\d{5,8}$")

    if not dot_pattern.match(dot_number):
        return Response(
            {"details": "invalid DOT number"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    URL = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{dot_number}?webKey={webkey}"

    res = requests.get(url=URL)
    data = res.json()

    if data["content"] is None or "allowedToOperate" not in data["content"]["carrier"]:
        return Response(
            [
                {
                    "details": """This DOT number is not registered in the FMCSA, 
                                            if you think this is a mistake please double check the number or contact the FMCSA"""
                },
            ],
            status=status.HTTP_404_NOT_FOUND,
        )

    if "allowedToOperate" in data["content"]["carrier"]:
        allowed_to_operate = data["content"]["carrier"]["allowedToOperate"]

        if allowed_to_operate == "Y":
            return True
        else:
            return Response(
                [
                    {
                        "details": "Carrier is not allowed to operate, if you think this is a mistake please contact the FMCSA"
                    },
                ],
                status=status.HTTP_403_FORBIDDEN,
            )


def check_mc_number(mc_number):

    client = secretmanager.SecretManagerServiceClient()
    webkey = client.access_secret_version(
        request={
            "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('FMCSA_WEBKEY')}/versions/1"
        }
    )
    webkey = webkey.payload.data.decode("UTF-8")
    mc_number_pattern = re.compile(r"^\d{5,8}$")

    if not mc_number_pattern.match(mc_number):
        return Response(
            {"details": "invalid MC number"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    URL = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={webkey}"
    res = requests.get(url=URL)
    data = res.json()
    if len(data["content"]) == 0:
        return Response(
            [
                {
                    "details": """This MC number is not registered in the FMCSA, 
                                    if you think this is a mistake please double check the number or contact the FMCSA"""
                }
            ],
            status=status.HTTP_404_NOT_FOUND,
        )

    if "allowedToOperate" in data["content"][0]["carrier"]:
        allowed_to_operate = data["content"][0]["carrier"]["allowedToOperate"]

        if allowed_to_operate.upper() == "Y":
            return True
        else:
            return Response(
                [
                    {
                        "details": "Dispatcher is not allowed to operate, if you think this is a mistake please contact the FMCSA"
                    }
                ],
                status=status.HTTP_403_FORBIDDEN,
            )
