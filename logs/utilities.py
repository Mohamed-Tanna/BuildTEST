import logs.models as models
import authentication.models as auth_models


def handle_log(user, action, model, details, log_fields=[]):
    app_user = auth_models.AppUser.objects.get(user=user)

    log_json = {}
    log_json["old"] = {}
    log_json["new"] = {}
    for field in log_fields:
        log_json["old"][field] = details["old"][field]
        log_json["new"][field] = details["new"][field]

    log = models.Log(app_user=app_user, action=action,
                     model=model, details=log_json)
    log.save()


def get_original_instance_and_original_request(request, instance):
    original_instance = {}
    original_request = {}
    for field in request.data:
        try:
            if str(getattr(instance, field)) != request.data[field]:
                original_instance[field] = str(getattr(instance, field))
                original_request[field] = request.data[field]
        except AttributeError:
            continue

    return original_instance, original_request