import re
from datetime import datetime , timezone
from pytz import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django_password_validators.settings import get_password_hasher
from django_password_validators.password_history.models import (
    PasswordHistory,
    UserPasswordHistoryConfig,
)
from password_config import config


class UniquePasswordsValidator(object):
    """
    Validate whether the password was once used by the user.

    The password is only checked for an existing user.
    """
    def __init__(self):
        self.history_password_memory = config["password_history"]

    def validate(self, password, user=None):

            if not user:
                return

            for user_config in UserPasswordHistoryConfig.objects.filter(user=user):
                password_hash = user_config.make_password_hash(password)
                for password_history_object in PasswordHistory.objects.filter(user_config=user_config).order_by("-date")[:self.history_password_memory]:
                    if password_history_object.password == password_hash:
                        raise ValidationError(
                            _(
                                "You can not use a password that was being used in the past {} passwords in this application.".format(
                                    self.history_password_memory)),
                            code='password_used'
                        )

                try:
                    used_password_object = PasswordHistory.objects.get(
                        user_config=user_config,
                        password=password_hash
                    )
                    used_password_object.date = datetime.now(timezone('UTC'))
                    used_password_object.save()
                    pass
                except PasswordHistory.DoesNotExist:
                    pass

    def password_changed(self, password, user=None):

        if not user:
            return

        user_config = UserPasswordHistoryConfig.objects.filter(
            user=user,
            iterations=get_password_hasher().iterations
        ).first()

        if not user_config:
            user_config = UserPasswordHistoryConfig()
            user_config.user = user
            user_config.save()

        password_hash = user_config.make_password_hash(password)

        # We are looking hash password in the database
        try:
            PasswordHistory.objects.get(
                user_config=user_config,
                password=password_hash
            )
        except PasswordHistory.DoesNotExist:
            ols_password = PasswordHistory()
            ols_password.user_config = user_config
            ols_password.password = password_hash
            ols_password.save()

    def get_help_text(self):
        return _('Your new password can not be identical to {} of the '
                 'previously entered.'.format(self.history_password_memory))





class NumberValidator(object):
    def __init__(self, min_digits=0):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if not len(re.findall('\d', password)) >= self.min_digits:
            raise ValidationError(
                _("The password must contain at least %(min_digits)d digit(s), 0-9."),
                code='password_no_number',
                params={'min_digits': self.min_digits},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_digits)d digit(s), 0-9." % {'min_digits': self.min_digits}
        )


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase letter, A-Z."
        )


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter, a-z."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 lowercase letter, a-z."
        )


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                _("The password must contain at least 1 symbol: " +
                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 symbol: " +
            "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
        )