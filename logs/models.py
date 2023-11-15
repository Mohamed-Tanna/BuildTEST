from django.db import models
import authentication.models as auth_models
# Create your models here.


class Log(models.Model):
    app_user = models.ForeignKey(
        to=auth_models.AppUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=100, null=False, blank=False)
    model = models.CharField(max_length=100, null=False, blank=False)
    details = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.app_user.user.username + " " + self.action + " " + self.model
