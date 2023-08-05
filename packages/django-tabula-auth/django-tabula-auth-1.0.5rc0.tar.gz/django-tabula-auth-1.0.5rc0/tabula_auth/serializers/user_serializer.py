from rest_framework import serializers
from tabula_auth.models import PhoneNumberUser

__all__ = [
    'UserCreateSerializer',
    'UserRetrieveSerializer',
    'AcceptTermsSerializer']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumberUser
        fields = ('phone_number', 'password', 'accept_terms')


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumberUser
        fields = ('phone_number', 'accept_terms')


class AcceptTermsSerializer(serializers.ModelSerializer):
    accept_terms = serializers.BooleanField()

    class Meta:
        model = PhoneNumberUser
        fields = ('accept_terms',)
