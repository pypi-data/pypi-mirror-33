from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from tests.serializers import UserObjectSerializer
from tests.models import UserObject

from generic.views import GenericViewset
from generic.factories import generic_factory
from generic.repositories import GenericRepository
from generic.validators import validate_many, is_value_unique
from generic.services import (generic_retrieve_single_service,
                              generic_retrieve_all_service,
                              generic_delete_service,
                              generic_update_service,
                              generic_create_service)


class ObjectViewSet(viewsets.ModelViewSet):
    repository = GenericRepository(UserObject)
    serializer_class = UserObjectSerializer

    def retrieve(self, request, pk=None, format=None):
        service = generic_retrieve_single_service(self.repository)

        view = GenericViewset(self.serializer_class, service, request)
        return view.retrieve(pk)

    def list(self, request, format=None):
        service = generic_retrieve_all_service(self.repository)

        view = GenericViewset(self.serializer_class, service, request)
        return view.list()

    def destroy(self, request, pk=None, format=None):
        service = generic_delete_service(self.repository)

        view = GenericViewset(self.serializer_class, service, request)
        return view.destroy(pk)

    def partial_update(self, request, pk=None, format=None):
        validators = (is_value_unique(self.repository, 'name'),)
        service = generic_update_service(self.repository, validate_many(*validators))

        view = GenericViewset(self.serializer_class, service, request)
        return view.partial_update(pk)

    def create(self, request, format=None):
        validators = (is_value_unique(self.repository, 'name'),)
        service = generic_create_service(self.repository, validate_many(*validators), generic_factory)

        view = GenericViewset(self.serializer_class, service, request)
        return view.create()