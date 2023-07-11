from django.contrib import admin
import invitation.models as models

class InvitationAdmin(admin.ModelAdmin):
    list_display = ["id", "inviter", "invitee", "created_at"]


admin.site.register(models.Invitation, InvitationAdmin)
