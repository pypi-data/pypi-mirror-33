from django.db.models.query import QuerySet
from utility.exceptions import ValidationError

def is_value_unique(repository, field):
    """
    Checks if a value is unique
    """
    def _checker(instance):
        if isinstance(instance, QuerySet):
            return all(_checker(i) for i in instance)
        else:
            i_dir = vars(instance)
            if repository.check_unique(instance.id, field, i_dir[field]):
                raise ValidationError('This value has alredy been used.', field=field)
            return True

    return _checker

def validate_many(*validators):
    """
    Allows to apply multiple validators
    """
    def _checker(instance):
        return all(validator(instance) for validator in validators)

    return _checker
