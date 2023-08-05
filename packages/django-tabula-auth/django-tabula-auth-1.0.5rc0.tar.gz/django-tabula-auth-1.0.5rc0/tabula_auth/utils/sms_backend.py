from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from rest_framework.exceptions import APIException

account_sid = getattr(settings, 'SMS_SID', None)
auth_token = getattr(settings, 'SMS_AUTH_TOKEN', None)
try:
    client = Client(account_sid, auth_token)
except TwilioException:
    client = None


def send(from_number, to_number, text):
    if not settings.TEST:
        if client:
            try:
                message = client.messages.create(
                    to=to_number,
                    from_=from_number,
                    body=text)
            except TwilioException as e:
                raise APIException(e)

        else:
            raise TwilioException
