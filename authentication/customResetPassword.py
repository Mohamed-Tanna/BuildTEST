#django imports
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site

#DRF imports
from rest_framework import serializers
from dj_rest_auth.forms import AllAuthPasswordResetForm
from dj_rest_auth.serializers import PasswordResetSerializer

#third party imports
from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import (user_pk_to_url_str, user_username)


class CustomAllAuthPasswordResetForm(AllAuthPasswordResetForm):
    def save(self, request, **kwargs):

        current_site = get_current_site(request)
        email = self.cleaned_data['email']
        token_generator = kwargs.get('token_generator', default_token_generator)

        for user in self.users:

            temp_key = token_generator.make_token(user)

            # send the password reset email
            path = reverse(
                'password_reset_confirm',
                args=[user_pk_to_url_str(user), temp_key],
            )
            my_domain = Site.objects.get(id=1)
            url = "https://"+f'{my_domain}'+ path

            context = {
                'current_site': current_site,
                'user': user,
                'password_reset_url': url,
                'request': request,
                'path': path
            }

            if app_settings.AUTHENTICATION_METHOD != app_settings.AuthenticationMethod.EMAIL:
                context['username'] = user_username(user)

            get_adapter(request).send_mail('account/email/password_reset_key', email, context)
        return self.cleaned_data['email']


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def update(self, instance, validated_data):
        """
            TODO
        """
        pass

    def create(self, validated_data):
        """
            TODO
        """
        pass

    def validate_email(self, value):
        # use the custom reset form
        self.reset_form = CustomAllAuthPasswordResetForm(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value