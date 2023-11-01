import logs.models as models
import authentication.models as auth_models

def handle_log(user, action, model, details, log_fields=[]):
    app_user = auth_models.AppUser.objects.get(user=user)
    log_string = ""
    for field in log_fields:
        log_string += field + ": " + str(details[field]) + "\n"
    log = models.Log(app_user=app_user, action=action,
                     model=model, details=log_string)
    log.save()
