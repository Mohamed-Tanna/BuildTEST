from django.db import models
from authentication.models import AppUser


class Invitation(models.Model):
    class InvitationStatusEnum(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    inviter = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    invitee = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=InvitationStatusEnum.choices,
        default=InvitationStatusEnum.PENDING,
        max_length=8,
    )

    def __str__(self):
        return f"{self.inviter} invited {self.invitee} at {self.created_at}"
