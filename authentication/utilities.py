import string, random
from rest_framework import status
from rest_framework.response import Response
from .models import Address


def create_address(building_number, street, city, state, country, zip_code):
    try:
        address = Address.objects.create(
            building_number=building_number,
            street=street,
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
                    random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(10)
                )           
    return identiefier
    