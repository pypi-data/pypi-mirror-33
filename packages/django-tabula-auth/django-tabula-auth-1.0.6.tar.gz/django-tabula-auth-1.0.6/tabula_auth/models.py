import datetime
import hashlib
import os
import random

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager, Group
from django.contrib.auth.hashers import check_password, make_password
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from .utils import Message
from django.core.cache import cache
from tabula_auth.exceptions import TabulaException, TabulaAuthException

__all__ = ['PhoneNumberUser', 'PhoneToken']


class PhoneNumberUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, phone_number, email,
                     password, **extra_fields):
        """
        Creates and saves a PhoneNumberUser with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        if not phone_number:
            phone_number = random.randint(1000000000, 9000000000)

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(
            username=username, email=email, phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, phone_number,
                    email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, phone_number, email, password,
                                 **extra_fields)

    def create_superuser(self, username, phone_number, email, password,
                         **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, phone_number, email, password,
                                 **extra_fields)


class PhoneNumberUser(AbstractUser, PermissionsMixin):
    is_superuser = models.BooleanField(default=False)
    phone_number = PhoneNumberField(unique=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    objects = PhoneNumberUserManager()
    REQUIRED_FIELDS = ['phone_number', 'email']
    accept_terms = models.BooleanField(default=False)
    demo_account = models.BooleanField(default=False)
    demo_otp = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.phone_number.as_international

    def cache_key(self):
        return f'new_for_{self.phone_number}'

    def change_number(self, new_number):
        otp = PhoneToken.generate_otp(length=getattr(
            settings, 'PHONE_LOGIN_OTP_LENGTH', 6))
        message = Message(
            template="Your code {code}",
            to_number=self.phone_number,
            code=otp
        )
        message.send()
        cache.set(self.cache_key(), {'phone': new_number,
                                     'otp': make_password(otp)})

        return otp

    def confirm_change(self, otp):
        new_phone = cache.get(self.cache_key())
        if check_password(otp, new_phone['otp']):
            self.phone_number = new_phone['phone']
            self.save()
            return self
        else:
            raise TabulaException('Bad otp')

    @property
    def is_authenticated(self):
        return True

    def check_group(self, group):
        try:
            self.groups.get(name=group)
            return True
        except Group.DoesNotExist:
            return False


class PhoneToken(models.Model):
    phone_number = PhoneNumberField(editable=False)
    otp = models.CharField(max_length=255, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    attempts = models.IntegerField(default=0)
    demo = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "OTP Token"
        verbose_name_plural = "OTP Tokens"

    def __str__(self):
        return self.phone_number.as_international

    @classmethod
    def create_otp_for_number(cls, number):

        today_min = datetime.datetime.combine(
            datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(
            datetime.date.today(), datetime.time.max)
        otps = cls.objects.filter(
            phone_number=number, timestamp__range=(
                today_min, today_max)).order_by('-timestamp')
        first_otp = cls.objects.filter(phone_number=number).order_by('-timestamp').first()

        def set_unactive(otp):
            otp.active = False
            otp.save()

        phone_login_attempts = getattr(settings, 'PHONE_LOGIN_ATTEMPTS', 10)
        phone_login_remain = getattr(settings, 'PHONE_LOGIN_REMAIN', 120)
        if otps.count() <= phone_login_attempts:
            if not otps or timezone.now() - otps.first().timestamp > datetime.timedelta(
                    seconds=phone_login_remain):
                if first_otp and first_otp.demo:
                    phone_token = first_otp
                    otp = phone_token.otp

                else:
                    [set_unactive(otp) for otp in cls.objects.filter(phone_number=number, active=True)]
                    otp = cls.generate_otp(
                        length=getattr(
                            settings,
                            'PHONE_LOGIN_OTP_LENGTH',
                            6))
                    phone_token = PhoneToken.objects.create(
                        phone_number=number, otp=make_password(otp))

                message = Message(
                    template=getattr(settings, 'LOGIN_CODE_MESSAGE', "Your login code: {code}"),
                    to_number=number,
                    code=otp
                )
                message.send()
                return phone_token, otp
            else:
                remain_time = datetime.timedelta(
                    seconds=phone_login_remain) - (timezone.now() - otps.first().timestamp)

                raise TabulaAuthException(remain_time.seconds, 'time_remain',
                                          f'Please wait {remain_time.seconds} seconds')
        else:
            raise TabulaAuthException(phone_login_attempts, 'login_attempts',
                                      f"You can not have more than {phone_login_attempts} attempts per day, please try again tomorrow")

    @classmethod
    def generate_otp(cls, length=6):
        hash_algorithm = getattr(
            settings,
            'PHONE_LOGIN_OTP_HASH_ALGORITHM',
            'sha256')
        m = getattr(hashlib, hash_algorithm)()
        m.update(getattr(settings, 'SECRET_KEY', None).encode('utf-8'))
        m.update(os.urandom(16))
        otp = str(int(m.hexdigest(), 16))[-length:]
        return otp

    def check_otp(self, otp):
        if self.demo:
            return self.otp == str(otp)
        else:
            return check_password(otp, self.otp)


@receiver(post_save, sender=PhoneNumberUser)
def update_demo_account(sender, instance=None, created=False, **kwargs):
    if instance.demo_account:
        token, _ = PhoneToken.objects.update_or_create(phone_number=instance.phone_number,
                                                       defaults={'demo': True,
                                                                 'otp': instance.demo_otp})


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
