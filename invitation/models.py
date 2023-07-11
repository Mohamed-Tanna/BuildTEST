from django.db import models
from authentication.models import AppUser

class Invitation(models.Model):
    inviter = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    invitee = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=[("pending", "pending"), ("accepted", "accepted"), ("rejected", "rejected")],
        default="pending",
        max_length=8,
    )

    def __str__(self):
        return f"{self.inviter} invited {self.invitee} at {self.created_at}"