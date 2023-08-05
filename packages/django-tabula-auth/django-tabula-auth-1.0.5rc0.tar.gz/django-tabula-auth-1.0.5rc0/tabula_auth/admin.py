from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, UserCreationForm, UserChangeForm
from .models import *
from django import forms


class TabulaUserCreationForm(UserCreationForm):
    class Meta:
        model = PhoneNumberUser
        fields = ("username", 'phone_number', 'demo_otp', 'demo_account')


class TabulaUserChangeForm(UserChangeForm):
    class Meta:
        model = PhoneNumberUser
        fields = ("username", 'phone_number', 'demo_otp', 'demo_account')


@admin.register(PhoneNumberUser)
class TabulaUserAdmin(UserAdmin):
    form = TabulaUserChangeForm
    add_form = TabulaUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'phone_number', 'demo_otp', 'demo_account'),
        }),
    )
    fieldsets = (('Phone Number Settings', {'fields': ('phone_number', 'demo_otp', 'demo_account')}),
                 ) + UserAdmin.fieldsets

    list_display = ('phone_number', 'demo_otp', 'demo_account') + UserAdmin.list_display
