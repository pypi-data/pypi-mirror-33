from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

class EmailNullField(models.EmailField):
    description = "EmailField that stores NULL"

    def get_db_prep_value(self, value, connection=None, prepared=False):
        value = super(EmailNullField, self).get_db_prep_value(value, connection, prepared)
        if value == "":
            return None
        else:
            return value


class PhoneNumberNullField(PhoneNumberField):
    description = "PhoneNumberField that stores NULL when empty"

    def get_db_prep_value(self, value, connection=None, prepared=False):
        value = super(PhoneNumberNullField, self).get_db_prep_value(value, connection, prepared)
        if value == "":
            return None
        else:
            return value

'''
from django.core.validators import RegexValidator
from django.forms import fields
from django.forms.fields import MultiValueField, CharField
class PhoneField(MultiValueField):
    def __init__(self, *args, **kwargs):
        # Define one message for all fields.
        error_messages = {
            'incomplete': 'Enter a country calling code and a phone number.',
        }
        # Or define a different message for each field.
        fields = (
            CharField(
                error_messages={'incomplete': 'Enter a country calling code.'},
                validators=[
                    RegexValidator(r'^[0-9]+$', 'Enter a valid country calling code.'),
                ],
            ),
            CharField(
                error_messages={'incomplete': 'Enter a phone number.'},
                validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.')],
            ),
            CharField(
                validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid extension.')],
                required=False,
            ),
        )
        super(PhoneField, self).__init__(
            error_messages=error_messages, fields=fields,
            require_all_fields=False, *args, **kwargs
        )
         
'''            