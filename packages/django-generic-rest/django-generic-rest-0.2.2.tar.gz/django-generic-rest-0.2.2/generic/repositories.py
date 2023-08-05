from django.core.exceptions import ObjectDoesNotExist

from utility.exceptions import ObjectNotFoundError
from utility.functions import contains_char_classes, is_email_valid

class GenericRepository():
    """
    Provides a generic database abstraction layer that does not depend on
    the model class
    """
    def __init__(self, model_class):
        """
        Constructor
        """
        self.model_class = model_class

    def find_by_user(self, user):
        """
        Provides generic find by user function
        """
        if hasattr(self.model_class, 'owner'):
            return self.model_class.objects.filter(owner=user)

        return self.model_class.objects.filter(id=user.id)

    def find_by_id(self, pk, user):
        """
        Provides generic find by id function
        """
        if hasattr(self.model_class, 'owner'):
            return self.model_class.objects.filter(owner=user).filter(id=pk)

        return self.model_class.objects.filter(id=user.id).filter(id=pk)

    def get_by_id(self, pk, user):
        """
        Provides generic get by id function
        """
        if hasattr(self.model_class, 'owner'):
            try:
                return self.model_class.objects.filter(owner=user).get(id=pk)
            except ObjectDoesNotExist:
                raise ObjectNotFoundError('Object not found.', modelclass=self.model_class)

        try:
            return self.model_class.objects.filter(id=user.id).get(id=pk)
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass=self.model_class)
        except AttributeError:
            raise ObjectNotFoundError('Object not found.', modelclass=self.model_class)

    def get_by_user_and_id(self, pk, user):
        """
        Provides generic get by user and id function
        """
        if hasattr(self.model_class, 'owner'):
            try:
                return self.model_class.objects.filter(owner=user).get(id=pk)
            except ObjectDoesNotExist:
                raise ObjectNotFoundError('Object not found.', modelclass=self.model_class)

        try:
            return self.model_class.objects.filter(id=user.id).get(id=pk)
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass=self.model_class)

    def get_all(self, user):
        """
        Provides generic get all function
        """
        if hasattr(self.model_class, 'owner'):
            return self.model_class.objects.filter(owner=user)

        try:
            return self.model_class.objects.filter(id=user.id)
        except AttributeError:
            raise ObjectNotFoundError('Object not found.', modelclass=self.model_class)

    def persist(self, instance):
        """
        Provides generic persist function
        """
        return instance.save()

    def delete_by_id(self, pk, user):
        """
        Provides generic delete function
        """
        if hasattr(self.model_class, 'owner'):
            try:
                return self.model_class.objects.filter(owner=user).get(id=pk).delete()
            except ObjectDoesNotExist:
                raise ObjectNotFoundError('Object not found.', modelclass=self.model_class)

        try:
            return self.model_class.objects.filter(id=user.id).get(id=pk).delete()
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass=self.model_class)

    def check_unique(self, pk, field, value):
        """
        Checks the uniqueness of value
        """
        if value is None:
            return 0

        kwargs = {field: str(value)}
        return self.model_class.objects.exclude(id=pk).filter(**kwargs)

    def check_password_too_short(self, password, length):
        """
        Checks if password is at least as long as length demands
        """
        if len(password) < length:
            return True

        return False

    def check_too_few_char_classes(self, password, noc):
        """
        Checks if password contains the demanded number of different
        char classes
        """
        if not contains_char_classes(password, noc):
            return True

        return False

    def check_email_valid(self, email):
        """
        Checks if an email address is valid
        """
        return email is None or is_email_valid(email)
