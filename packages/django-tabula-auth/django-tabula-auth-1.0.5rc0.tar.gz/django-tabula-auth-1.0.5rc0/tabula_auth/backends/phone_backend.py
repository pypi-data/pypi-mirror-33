import uuid

from django.contrib.auth import get_user_model

from django.contrib.auth.backends import ModelBackend

from ..models import PhoneToken
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
from tabula_auth.exceptions import TabulaAuthException

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def user_detail(user, last_login):
    try:
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
    except BaseException:
        token = Token.objects.create(user=user)
        token = token.key
    user_json = {
        "id": user.pk,
        "last_login": last_login,
        "token": token,
        "status": status.HTTP_200_OK,
        'accept_terms': user.accept_terms
    }
    return user_json


def model_field_attr(model, model_field, attr):
    """
    Returns the specified attribute for the specified field on the model class.
    """
    fields = dict([(field.name, field) for field in model._meta.fields])
    return getattr(fields[model_field], attr)


class PhoneBackend(ModelBackend):
    def __init__(self, *args, **kwargs):
        self.user_model = get_user_model()

    def get_phone_number_data(self, phone_number):
        """
        Method used for filtering query.
        """
        phone_number_field = 'phone_number'
        data = {
            phone_number_field: phone_number
        }
        return data

    def get_username(self):
        """
        Returns a UUID-based 'random' and unique username.

        This is required data for user models with a username field.
        """
        return str(uuid.uuid4())[:model_field_attr(
            self.user_model, 'username', 'max_length')]

    def create_user(self, phone_token=None, phone_number=None, **extra_fields):
        """
        Create and returns the user based on the phone_token.
        """
        assert phone_number or phone_token, 'Phone token or phone number must provided'
        password = self.user_model.objects.make_random_password()

        username = extra_fields.get('username', self.get_username())
        password = extra_fields.get('password', password)
        phone_number = phone_token.phone_number if phone_token else phone_number

        extra_fields.update({
            'username': username,
            'password': password,
        })
        extra_fields.update(self.get_phone_number_data(phone_number))
        user = self.user_model.objects.create_user(**extra_fields)
        return user

    def authenticate(self, request, pk=None, otp=None, phone_number=None, **extra_fields):

        # 1. Validating the PhoneToken with PK and OTP.
        # 2. Check if phone_token and otp are same, within the given time range
        if otp:
            try:
                if pk:
                    phone_token = PhoneToken.objects.get(
                        pk=pk,
                        active=True
                    )
                elif phone_number:
                    phone_token = PhoneToken.objects.filter(
                        phone_number=phone_number,
                        active=True
                    ).first()
                else:
                    raise TabulaAuthException('Phone number or OTP not provided', 'phone_number_otp_not_provided')
                if not phone_token.check_otp(otp):
                    raise PhoneToken.DoesNotExist
            except PhoneToken.DoesNotExist:
                phone_token = PhoneToken.objects.get(pk=pk)
                phone_token.attempts = phone_token.attempts + 1
                phone_token.save()
                raise PhoneToken.DoesNotExist

            # 3. Create new user if he doesn't exist. But, if he exists login.
            user = self.user_model.objects.filter(
                **self.get_phone_number_data(phone_token.phone_number)
            ).first()

            if not user:
                user = self.create_user(
                    phone_token=phone_token,
                    **extra_fields
                )
            phone_token.attempts += 1
            phone_token.save()
            return user
        else:
            return super(self.__class__, self).authenticate(
                request, **extra_fields, )
