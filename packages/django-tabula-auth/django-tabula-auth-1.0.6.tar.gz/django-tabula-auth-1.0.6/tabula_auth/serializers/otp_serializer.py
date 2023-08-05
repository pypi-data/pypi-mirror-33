from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField
from rest_framework import serializers

from tabula_auth.models import PhoneToken

User = get_user_model()

__all__ = [
    'PhoneTokenCreateSerializer',
    'PhoneTokenUser',
    'PhoneTokenValidateSerializer']


class PhoneTokenCreateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        validators=PhoneNumberField().validators)

    class Meta:
        model = PhoneToken
        fields = ('pk', 'phone_number')


class PhoneTokenUser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class PhoneTokenValidateSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    phone_number = serializers.CharField(
        validators=PhoneNumberField().validators, required=False)
    otp = serializers.CharField(max_length=40)

    class Meta:
        model = PhoneToken
        fields = ('pk', 'otp', 'phone_number')


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        return validated_data
