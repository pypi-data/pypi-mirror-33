from django.conf import settings
from .sms_backend import send

__all__ = ['Message']


class Message:
    from_number = getattr(settings, 'FROM_PHONE', '')

    def __init__(self, template, to_number, **kwargs):
        self.text = template.format(**kwargs)
        self.to_number = to_number

    def get_backend(self):
        pass

    def send(self):
        send(self.from_number, self.to_number, self.text)
