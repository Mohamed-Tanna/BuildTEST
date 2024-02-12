import os
import random
import string
from datetime import datetime, timedelta

import environ
import rest_framework.exceptions as exceptions
from django.apps import apps
from django.db.models import Q
from google.auth.transport import requests
from google.oauth2 import id_token
import authentication.models as auth_models
import shipment.models as models
from document.utilities import get_signing_creds
from freightmonster.classes import StorageClient, SecreteManagerClient
from freightmonster.constants import CREATED, AWAITING_CUSTOMER, AWAITING_CARRIER, ASSIGNING_CARRIER, \
    AWAITING_DISPATCHER, CLAIM_CREATED, GS_DEV_FREIGHT_UPLOADED_FILES_BUCKET_NAME
from freightmonster.settings import BASE_DIR
from freightmonster.thread import ThreadWithReturnValue
from notifications.utilities import handle_notification


def get_shipment_party_by_username(username):
    try:
        user = auth_models.User.objects.get(username=username)
        user = auth_models.AppUser.objects.get(user=user.id)
        user = auth_models.ShipmentParty.objects.get(app_user=user.id)
        return user
    except (
            auth_models.User.DoesNotExist,
            auth_models.AppUser.DoesNotExist,
            auth_models.ShipmentParty.DoesNotExist,
    ):
        raise exceptions.NotFound(detail="shipment party does not exist.")
    except BaseException as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise exceptions.ParseError(detail=f"{e.args[0]}")


def get_carrier_by_username(username):
    try:
        user = auth_models.User.objects.get(username=username)
        user = auth_models.AppUser.objects.get(user=user.id)
        user = auth_models.Carrier.objects.get(app_user=user.id)
        return user
    except (
            auth_models.User.DoesNotExist,
            auth_models.AppUser.DoesNotExist,
            auth_models.Carrier.DoesNotExist,
    ):
        raise exceptions.NotFound(detail="carrier does not exist.")
    except BaseException as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise exceptions.ParseError(detail=f"{e.args[0]}")


def get_dispatcher_by_username(username):
    try:
        user = auth_models.User.objects.get(username=username)
        user = auth_models.AppUser.objects.get(user=user.id)
        user = auth_models.Dispatcher.objects.get(app_user=user.id)
        return user
    except (
            auth_models.User.DoesNotExist,
            auth_models.AppUser.DoesNotExist,
            auth_models.Dispatcher.DoesNotExist,
    ):
        raise exceptions.NotFound(detail="dispatcher does not exist.")
    except BaseException as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise exceptions.ParseError(detail=f"{e.args[0]}")


def get_app_user_by_username(username):
    try:
        user = auth_models.User.objects.get(username=username)
        user = auth_models.AppUser.objects.get(user=user.id)
        return user
    except (auth_models.User.DoesNotExist, auth_models.AppUser.DoesNotExist):
        raise exceptions.NotFound(detail="app user does not exist.")
    except BaseException as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise exceptions.ParseError(detail=f"{e.args[0]}")


def generate_load_name() -> string:
    name = "L-" + (
        "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    )
    return name


def generate_shipment_name() -> string:
    name = "SH-" + (
        "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    )
    return name


def get_company_by_role(app_user, user_type="user"):
    try:
        company = None
        if app_user.user_type == "manager":
            company = auth_models.Company.objects.get(manager=app_user)
        else:
            company_employee = auth_models.CompanyEmployee.objects.get(app_user=app_user)
            company = auth_models.Company.objects.get(id=company_employee.company.id)
        return company
    except auth_models.CompanyEmployee.DoesNotExist:
        raise exceptions.NotFound(detail=f"{user_type} has no company")
    except BaseException as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise exceptions.ParseError(detail=f"{e.args[0]}")


def get_user_tax_by_role(app_user, user_type="user"):
    try:
        return auth_models.UserTax.objects.get(app_user=app_user)
    except auth_models.UserTax.DoesNotExist:
        raise exceptions.NotFound(detail=f"{user_type} has no tax information")
    except BaseException as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise exceptions.ParseError(detail=f"{e.args[0]}")


def get_user_tax_or_company(app_user, user_type="user"):
    """Returns the company or user tax of the user"""
    try:
        return get_company_by_role(app_user, user_type=user_type)
    except (exceptions.NotFound, exceptions.ParseError):
        pass

    try:
        return get_user_tax_by_role(app_user, user_type=user_type)
    except (exceptions.NotFound, exceptions.ParseError):
        pass

    raise exceptions.NotFound(
        detail=f"{user_type} has no tax information or a company."
    )


def check_parties_tax_info(customer_username, dispatcher_username):
    customer_app_user = get_app_user_by_username(customer_username)
    dispatcher_app_user = get_app_user_by_username(dispatcher_username)
    get_user_tax_or_company(customer_app_user, user_type="customer")
    get_user_tax_or_company(dispatcher_app_user, user_type="dispatcher")

    return True


def extract_billing_info(billing_info, party):
    if isinstance(billing_info, auth_models.Company):
        billing_info = {
            "name": billing_info.name,
            "address": billing_info.address.address
                       + ", "
                       + billing_info.address.city
                       + ", "
                       + billing_info.address.state
                       + ", "
                       + billing_info.address.zip_code,
            "phone_number": billing_info.phone_number,
        }
    if isinstance(billing_info, auth_models.UserTax):
        billing_info = {
            "name": party.app_user.user.first_name
                    + ", "
                    + party.app_user.user.last_name,
            "address": billing_info.address.address
                       + ", "
                       + billing_info.address.city
                       + ", "
                       + billing_info.address.state
                       + ", "
                       + billing_info.address.zip_code,
            "phone_number": party.app_user.phone_number,
        }

    return billing_info


def is_app_user_customer_of_load(app_user: auth_models.AppUser, load: models.Load):
    if load.customer.app_user == app_user:
        return True
    return False


def is_app_user_dispatcher_of_load(app_user: auth_models.AppUser, load: models.Load):
    if load.dispatcher.app_user == app_user:
        return True
    return False


def is_app_user_carrier_of_load(app_user: auth_models.AppUser, load: models.Load):
    if load.carrier.app_user == app_user:
        return True
    return False


def send_notifications_to_load_parties(load: models.Load, action, event=None, claim: models.Claim = None):
    notified_usernames = set()
    roles = ["dispatcher", "shipper", "consignee", "customer"]

    for role in roles:
        actor = getattr(load, role)
        app_user = actor.app_user
        username = app_user.user.username

        if username not in notified_usernames:
            if event == "load_created" and username == load.created_by.user.username:
                continue
            if event == "load_created":
                handle_notification(
                    action=action, app_user=app_user, load=load, sender=load.created_by
                )
            elif event == CLAIM_CREATED:
                handle_notification(
                    action=action,
                    app_user=app_user,
                    load=load,
                    sender=claim.claimant
                )
            elif event == "load_status_changed":
                handle_notification(
                    action=action, app_user=app_user, load=load)
            notified_usernames.add(username)


def apply_load_access_filters_for_user(filter_query, app_user: auth_models.AppUser):
    if app_user.selected_role == "shipment party":
        try:
            shipment_party = models.ShipmentParty.objects.get(app_user=app_user.id)
            filter_query |= (
                    Q(shipper=shipment_party.id)
                    | Q(consignee=shipment_party.id)
                    | Q(customer=shipment_party.id)
            )
        except models.ShipmentParty.DoesNotExist:
            pass

    elif app_user.selected_role == "dispatcher":
        try:
            dispatcher = models.Dispatcher.objects.get(app_user=app_user.id)
            filter_query |= Q(dispatcher=dispatcher.id)
        except models.Dispatcher.DoesNotExist:
            pass

    elif app_user.selected_role == "carrier":
        try:
            carrier = models.Carrier.objects.get(app_user=app_user.id)
            filter_query |= Q(carrier=carrier.id)
        except models.Carrier.DoesNotExist:
            pass

    return filter_query


def get_load_party_by_id(load, app_user_id):
    load_parties = {
        "customer": load.customer,
        "shipper": load.shipper,
        "dispatcher": load.dispatcher,
        "carrier": load.carrier,
        "consignee": load.consignee
    }
    for key, value in load_parties.items():
        if value is not None and value.app_user.id == app_user_id:
            return value
    return None


def is_there_claim_for_load_id(load_id):
    try:
        models.Claim.objects.get(load=load_id)
        return True
    except models.Claim.DoesNotExist:
        return False


def is_load_status_valid_to_create_claim(status):
    return not (
            status == CREATED or
            status == AWAITING_CUSTOMER or
            status == AWAITING_CARRIER or
            status == ASSIGNING_CARRIER or
            status == AWAITING_DISPATCHER
    )


def get_unique_symbol_algorithm_id(length):
    symbols = string.ascii_letters + string.digits + "-*=+_&%$#@!"
    return ''.join(random.choice(symbols) for _ in range(length))


def get_unique_name_for_supporting_docs(bucket, file_name):
    final_file_name = file_name
    blob = bucket.blob("images/" + final_file_name)
    while blob.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = get_unique_symbol_algorithm_id(20)
        final_file_name = f"{timestamp}_{unique_id}_{final_file_name}"
        blob = bucket.blob("images/" + final_file_name)
        final_file_name = file_name
    return final_file_name


def upload_claim_supporting_docs_to_gcs(uploaded_file, bucket):
    file_name = get_unique_name_for_supporting_docs(bucket, uploaded_file.name)
    blob = bucket.blob(f"images/{file_name}")
    blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)
    return file_name


def generate_signed_url_for_claim_supporting_docs(object_name, bucket, storage_client, expiration=3600):
    bucket_name = GS_DEV_FREIGHT_UPLOADED_FILES_BUCKET_NAME
    try:
        blob = bucket.blob("images/" + object_name)
        if not blob.exists():
            raise NameError
        signing_creds = get_signing_creds(storage_client._credentials)
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.utcnow() + timedelta(seconds=expiration),
            method="GET",
            credentials=signing_creds,
        )
        return url
    except NameError:
        print(f"Error: Object {object_name} not found in bucket {bucket_name}")
        return None
    except (BaseException) as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return None


def can_company_manager_see_load(load: models.Load, manager: models.AppUser):
    load_parties = [
        load.customer,
        load.shipper,
        load.dispatcher,
        load.consignee,
        load.carrier
    ]
    manager_company = auth_models.Company.objects.get(manager=manager)
    for party in load_parties:
        try:
            auth_models.CompanyEmployee(app_user=party.app_user, company=manager_company)
            return True
        except auth_models.CompanyEmployee.DoesNotExist:
            return False
    return False


def get_load_parties_under_company_manager(load: models.Load, manager: models.AppUser):
    load_parties = [
        load.customer,
        load.shipper,
        load.dispatcher,
        load.consignee,
        load.carrier
    ]
    manager_company = auth_models.Company.objects.get(manager=manager)
    result = []
    for party in load_parties:
        try:
            auth_models.CompanyEmployee(app_user=party.app_user, company=manager_company)
            if result.index(party.app_user) == -1:
                result.append(party.app_user)
        except auth_models.CompanyEmployee.DoesNotExist:
            continue
    return result


def get_app_user_load_party_roles(app_user: auth_models.AppUser, load: models.Load):
    result = []
    party_roles = {
        "customer": load.customer,
        "shipper": load.shipper,
        "dispatcher": load.dispatcher,
        "carrier": load.carrier,
        "consignee": load.consignee,
    }
    for role, party in party_roles.items():
        if party and party.app_user and party.app_user.id == app_user.id:
            result.append(role)
    return result


def does_load_have_other_load_parties(app_user: auth_models.AppUser, load: models.Load):
    if len(get_app_user_load_party_roles(app_user=app_user, load=load)) == 5:
        return False
    return True


def does_user_have_claim_note_on_claim_already(app_user: auth_models.AppUser, claim: models.Claim):
    try:
        models.ClaimNote.objects.get(claim=claim, creator=app_user)
        return True
    except models.ClaimNote.DoesNotExist:
        return False


def is_user_the_creator_of_the_claim(app_user: auth_models.AppUser, claim: models.Claim):
    return claim.claimant == app_user


def upload_supporting_docs(supporting_docs):
    storage_client = StorageClient().storage_client
    bucket = storage_client.get_bucket(GS_DEV_FREIGHT_UPLOADED_FILES_BUCKET_NAME)
    threads = []
    new_supporting_docs_name = []
    for doc in supporting_docs:
        doc_name = f"supporting_docs_{doc.name}"
        doc.name = doc_name
        thread = ThreadWithReturnValue(
            target=upload_claim_supporting_docs_to_gcs,
            args=(doc, bucket,)
        )
        thread.start()
        threads.append(thread)
    for thread in threads:
        new_supporting_docs_name.append(thread.join())
    return new_supporting_docs_name


def get_supporting_docs_info(supporting_docs):
    storage_client = StorageClient().storage_client
    bucket = storage_client.get_bucket(GS_DEV_FREIGHT_UPLOADED_FILES_BUCKET_NAME)
    supporting_docs_info = []
    threads = []
    for doc in supporting_docs:
        thread = ThreadWithReturnValue(
            target=generate_signed_url_for_claim_supporting_docs,
            args=(doc, bucket, storage_client,)
        )
        thread.start()
        threads.append(thread)
        supporting_docs_info.append(
            {
                "name": doc,
                "url": ""
            }
        )
    for i in range(len(threads)):
        supporting_docs_info[i]["url"] = threads[i].join()
    return supporting_docs_info


def generate_new_unique_file_name(file_name, prefix=""):
    splited_file_name = file_name.split(".")
    return f'{splited_file_name[0]}_{prefix}{datetime.now().strftime("%Y%m%d%H%M%S")}_{get_unique_symbol_algorithm_id(20)}.{splited_file_name[-1]}'


def get_unique_blob(bucket, file_name, list_of_names_to_compare=list, path_name=""):
    while True:
        new_unique_attachment_name = generate_new_unique_file_name(
            file_name=file_name,
            prefix="load_note_attachment_"
        )
        blob = bucket.blob(f"{path_name}{new_unique_attachment_name}")
        if not blob.exists() and new_unique_attachment_name not in list_of_names_to_compare:
            break
    return blob


def generate_put_signed_url_for_file(
        blob,
        content_type,
        storage_client=None,
        expiration_time=900,
        headers=None
):
    if storage_client is None:
        storage_client = StorageClient().storage_client
    signing_creds = get_signing_creds(storage_client._credentials)
    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.utcnow() + timedelta(seconds=expiration_time),
        method="PUT",
        content_type=content_type,
        headers=headers,
        # credentials=signing_creds,
    )
    return url


def generate_get_signed_url_for_file(
        blob,
        storage_client=None,
        expiration_time=3600
):
    if storage_client is None:
        storage_client = StorageClient().storage_client
    signing_creds = get_signing_creds(storage_client._credentials)
    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.utcnow() + timedelta(seconds=expiration_time),
        method="GET",
        # credentials=signing_creds,
    )
    return url


def is_user_one_of_load_parties(app_user, load):
    user_load_party = get_load_party_by_id(load, app_user.id)
    if user_load_party is None:
        return False
    return True


def delete_keys_from_dictionary(dictionary, keys):
    for key in keys:
        if key in dictionary:
            del dictionary[key]


def get_load_parties_role_id(load_parties_app_user_ids):
    result = {}
    for role, app_user_id in load_parties_app_user_ids.items():
        actual_role = role
        if role in ["customer", "shipper", "consignee"]:
            actual_role = "ShipmentParty"
        model = apps.get_model("authentication", actual_role.capitalize())
        if model is not None:
            result[role] = model.objects.get(app_user__id=app_user_id).id
    return result


def extract_load_parties_info(data):
    available_load_party_roles = ["customer", "shipper", "dispatcher", "carrier", "consignee"]
    result = {}
    for key, value in data.items():
        if key in available_load_party_roles:
            result[key] = value
    return result


def is_ocid_token_valid(token):
    try:
        data = id_token.verify_oauth2_token(
            token,
            requests.Request(),
        )
        if (
                data["email"] == get_cloud_scheduler_email() and
                data["email_verified"] and
                data["iss"] == "https://accounts.google.com" and
                data["exp"] < (datetime.now().timestamp() * 1000)
        ):
            return True
        return False
    except ValueError:
        return False


def get_cloud_scheduler_email():
    if os.getenv("ENV") == "LOCAL":
        env = environ.Env()
        env.read_env(os.path.join(BASE_DIR, "local.env"))
        return env("CLOUD_SCHEDULER_EMAIL")
    else:
        return SecreteManagerClient().get_secret_value("cloud_scheduler_email")
