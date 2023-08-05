from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from tabula_auth.exceptions import TabulaAuthException
from tabula_auth.models import PhoneToken
from tabula_auth.serializers import (
    PhoneTokenCreateSerializer, PhoneTokenValidateSerializer
)
from django.conf import settings
from tabula_auth.backends.phone_backend import user_detail
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
__all__ = ['GenerateOTP', 'ValidateOTP']


class GenerateOTP(CreateAPIView):
    """
    Сгенерировать новый код
    """
    queryset = PhoneToken.objects.all()
    serializer_class = PhoneTokenCreateSerializer

    def post(self, request, format=None):
        # Get the patient if present or result None.
        ser = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        if ser.is_valid():
            try:
                token, otp = PhoneToken.create_otp_for_number(
                    request.data.get('phone_number')
                )
                print(otp)
                logger.error(otp)
                phone_token = self.serializer_class(
                    token, context={'request': request}
                )
                return Response(phone_token.data)

            except TabulaAuthException as e:
                return Response({
                    'detail': e.__str__(),
                    'error_type': e.error_type,
                    'count': e.count
                }, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {'reason': ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ValidateOTP(CreateAPIView):
    """
    Проверить код
    """
    queryset = PhoneToken.objects.all()
    serializer_class = PhoneTokenValidateSerializer

    def post(self, request, format=None):
        # Get the patient if present or result None.

        ser = self.serializer_class(
            data=request.data, context={'request': request}
        )
        if ser.is_valid():
            pk = request.data.get("pk")
            otp = request.data.get("otp", None)
            phone_number = request.data.get("phone_number", None)
            try:
                user = authenticate(request, pk=pk, otp=otp, phone_number=phone_number)
                if user:
                    last_login = user.last_login
                else:
                    last_login = timezone.now()
                login(request, user)
                response = user_detail(user, last_login)
                return Response(response, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(
                    {'reason': getattr(settings, 'OTP_NOT_FOUND_TEXT',
                                       "The sms code wasn't correct. Please check and try again.")},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
        return Response(
            {'reason': ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
