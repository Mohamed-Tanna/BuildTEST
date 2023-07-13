import os
# DRF imports
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.mixins import ListModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
# Django imports
from django.shortcuts import get_object_or_404
# Modules' imports
import invitation.models as models
import invitation.utilities as utils
import shipment.models as ship_models
from authentication.models import User
import invitation.serializers as serializers
import shipment.serializers as ship_serializers
import authentication.permissions as permissions
if os.getenv("ENV") == "DEV":
    from freightmonster.settings.dev import BASE_URL
elif os.getenv("ENV") == "STAGING":
    from freightmonster.settings.staging import BASE_URL
else:
    from freightmonster.settings.local import BASE_URL


class InvitationsHandlingView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = serializers.InvitationsSerializer
    queryset = models.Invitation.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "action" not in request.data or "id" not in request.data:
            return Response(
                [{"details": "id and action fields are required"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation_id = request.data["id"]
        action = request.data["action"]
        invitation = get_object_or_404(
            models.Invitation, id=invitation_id, status="pending"
        )
        if invitation.invitee != request.user.email:
            return Response(
                [{"details": "you do not have permission to edit this resource."}],
                status=status.HTTP_403_FORBIDDEN,
            )
        if action == "accept":
            invitee_user = get_object_or_404(User, email=invitation.invitee)
            invitee_app_user = get_object_or_404(models.AppUser, user=invitee_user)
            iniviter_contact = ship_models.Contact.objects.create(
                origin=invitation.inviter.user, contact=invitee_app_user
            )
            invitee_contact = ship_models.Contact.objects.create(
                origin=invitee_user, contact=invitation.inviter
            )
            invitation.status = "accepted"
            invitation.save()
            data = {
                "inviter": ship_serializers.ContactCreateSerializer(
                    iniviter_contact
                ).data,
                "invitee": ship_serializers.ContactCreateSerializer(
                    invitee_contact
                ).data,
            }
            return Response(status=status.HTTP_201_CREATED, data=data)

        elif action == "reject":
            invitation.status = "rejected"
            invitation.save()
            return Response(
                status=status.HTTP_200_OK,
                data=serializers.InvitationsSerializer(invitation).data,
            )
        
        else:
            return Response(
                [{"details": "invalid action"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_queryset(self):
        queryset = self.queryset
        target = self.request.query_params.get("target", "all")
        assert queryset is not None, (
            "'%s' should either include a `queryset` attribute, or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        app_user = get_object_or_404(models.AppUser, user=self.request.user)
        if target=="all":
            queryset = models.Invitation.objects.filter(inviter=app_user)
        elif target == "pending" or target == "accepted" or target == "rejected":
            queryset = models.Invitation.objects.filter(inviter=app_user, status=target)
        else:
            queryset = models.Invitation.objects.none()
        return queryset


class CreateInvitationView(GenericAPIView):
    permission_classes = [IsAuthenticated, permissions.IsAppUser]
    serializer_class = serializers.InvitationsSerializer
    queryset = models.Invitation.objects.all()

    def get(self, request, *args, **kwargs):
        app_user = models.AppUser.objects.get(user=self.request.user)
        queryset = models.Invitation.objects.filter(
            invitee=app_user.user.email, status="pending"
        )
        if not queryset.exists():
            return Response(
                {"detail": "No invitations found for the user."},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    def post(self, request, *args, **kwargs):
        if "invitee" not in request.data:
            return Response(
                [{"details": "invitee field is required"}],
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitee_email = request.data["invitee"]
        try:
            User.objects.get(email=invitee_email)
            return Response(
                {"details": "user already exists, try adding them as a contact."},
                status=status.HTTP_409_CONFLICT,
            )
        except User.DoesNotExist:
            inviter_app_user = get_object_or_404(models.AppUser, user=request.user)
            try:
                models.Invitation.objects.get(inviter=inviter_app_user, invitee=invitee_email)
                return Response(data={"details": "you have already sent an invite to this email."}, status=status.HTTP_409_CONFLICT)
            except models.Invitation.DoesNotExist:   
                invitation = models.Invitation.objects.create(
                    inviter=inviter_app_user, invitee=invitee_email
                )
                invitation.save()
                utils.send_invite(
                    subject="Invitation to Join Freight Slayer",
                    template="send_invite.html",
                    to=invitee_email,
                    inviter_email=invitation.inviter.user.email,
                    url=f"{BASE_URL}/register/",
                )
                return Response(
                    status=status.HTTP_201_CREATED,
                    data=serializers.InvitationsSerializer(invitation).data,
                )
        except (BaseException) as e:
            print(f"Unexpected {e=}, {type(e)=}")
            return Response(
                {"details": "something went wrong - CrINV."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
