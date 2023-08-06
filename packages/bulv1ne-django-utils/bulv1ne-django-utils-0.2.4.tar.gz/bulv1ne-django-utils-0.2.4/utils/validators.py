from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text


@deconstructible
class EmailListValidator(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, value):
        email_list = force_text(value).split()
        email_validator = EmailValidator(*self.args, **self.kwargs)
        for email in email_list:
            try:
                email_validator(email)
            except ValidationError as e:
                raise ValidationError(
                    '"{}" is not a valid email'.format(email),
                    code=e.code,
                )
