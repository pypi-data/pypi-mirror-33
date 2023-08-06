from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet

from utility.exceptions import ValidationError


def is_password_length_sufficient(repository, length):
    """
    Checks if the length of a user's password contains at least length
    characters
    """

    def _checker(instance):
        if isinstance(instance, QuerySet):
            return all(_checker(i) for i in instance)
        else:
            # print("instance: {0}".format(repr(instance)))
            if repository.check_password_too_short(instance.password, length):
                raise ValidationError(
                    """Password is not long enough. Minimal length: 
                       {0} characters.""".format(length),
                    field='password')
            return True

    return _checker


def does_contain_char_classes(repository, noc):
    """
    Checks if the user's password contains noc different character classes
    """
    if noc < 0 or noc > 4:
        raise ImproperlyConfigured("""Number of character classes must be 
                                      in range 0-4.""")

    def _checker(instance):
        if isinstance(instance, QuerySet):
            return all(_checker(i) for i in instance)
        else:
            if repository.check_too_few_char_classes(instance.password, noc):
                raise ValidationError(
                    ("The password must contain {0} of the following "
                     "characters: upper case letters, lower case letters, "
                     "digits and special characters.").format(noc),
                    field='password')
            return True

    return _checker


def is_email_valid(repository):
    """
    Checks is a user's email address is valid
    """

    def _checker(instance):
        if isinstance(instance, QuerySet):
            return all(_checker(i) for i in instance)
        else:
            if not repository.check_email_valid(instance.email):
                raise ValidationError('This email address is invalid.',
                                      field='email')
            return True

    return _checker
