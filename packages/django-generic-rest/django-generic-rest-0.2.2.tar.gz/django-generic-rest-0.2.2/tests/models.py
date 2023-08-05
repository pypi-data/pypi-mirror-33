from django.db import models

from authentication.models import User
from utility.functions import (get_current_datetime, get_uuid1)
from utility.mixins import DictMixin

class Object(models.Model, DictMixin):
    id = models.UUIDField(default=get_uuid1, primary_key=True)
    name = models.CharField(unique=True, max_length=255, blank=False, null=False)
    password = models.CharField(unique=False, max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'object'


class UserObject(models.Model, DictMixin):
    id = models.UUIDField(default=get_uuid1, primary_key=True)
    owner = models.ForeignKey(
        'authentication.User', models.CASCADE, related_name='user_objects')
    name = models.CharField(unique=True, max_length=255, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'user_object'


class UserObjectPw(models.Model, DictMixin):
    id = models.UUIDField(default=get_uuid1, primary_key=True)
    owner = models.ForeignKey(
        'authentication.User', models.CASCADE, related_name='user_objects_pw')
    name = models.CharField(unique=True, max_length=255, blank=False, null=False)
    password = models.CharField(unique=False, max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_object_pw'