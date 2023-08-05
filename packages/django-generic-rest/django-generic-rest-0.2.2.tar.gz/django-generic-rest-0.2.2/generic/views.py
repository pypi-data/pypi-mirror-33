import logging

from django.conf import settings

from rest_framework import status
from rest_framework.response import Response

from utility.exceptions import ObjectNotFoundError, ValidationError
from utility.logger import get_log_msg

LOGGER = logging.getLogger('views')

def handle_error(error, status_code):
    """
    General error handler with error message and http error code being passed
    """
    content = {settings.ERROR_KEY: str(error)}
    return Response(content, status=status_code)

class GenericViewset:
    """
    Provides generic functionality for http post, get, patch and delete calls
    """
    serializer_class = None
    service = None
    request = None

    def __init__(self, serializer_class, service, request):
        self.serializer_class = serializer_class
        self.service = service
        self.request = request

    def create(self):
        """
        Creates and persists passed object if valid
        """
        LOGGER.info(get_log_msg(self.request, self.request.user))
        data = self.request.data
        serializer = self.serializer_class(data=data, many=False)
        if serializer.is_valid():
            return self._create_instance(**serializer.data)

        return handle_error('Validation failed.', status.HTTP_400_BAD_REQUEST)

    def _create_instance(self, **data):
        try:
            instance = self.service(user=self.request.user, **data)
            serializer = self.serializer_class(instance=instance, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as error:
            return handle_error(error, status.HTTP_400_BAD_REQUEST)
        except ObjectNotFoundError as error:
            return handle_error(error, status.HTTP_404_NOT_FOUND)

    def list(self):
        """
        Retrieves all objects returned by the provided service
        """
        LOGGER.info(get_log_msg(self.request, self.request.user))
        return self._list_instances()

    def _list_instances(self):
        instances = self.service(user=self.request.user)
        serializer = self.serializer_class(instance=instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, key):
        """
        Retrieves a single object by its primary key
        """
        LOGGER.info(get_log_msg(self.request, self.request.user))
        return self._retrieve_instance(key)

    def _retrieve_instance(self, key):
        try:
            instance = self.service(key, user=self.request.user)
            serializer = self.serializer_class(instance=instance, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectNotFoundError as error:
            return handle_error(error, status.HTTP_404_NOT_FOUND)

    def destroy(self, key):
        """
        Deletes a single object by its primary key
        """
        LOGGER.info(get_log_msg(self.request, self.request.user))
        return self._destroy_instance(key)

    def _destroy_instance(self, key):
        try:
            instance = self.service(key, user=self.request.user)
            serializer = self.serializer_class(instance=instance, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectNotFoundError as error:
            return handle_error(error, status.HTTP_404_NOT_FOUND)

    def partial_update(self, key):
        """
        Partially updates an existing object without overwritung it
        """
        LOGGER.info(get_log_msg(self.request, self.request.user))
        data = self.request.data
        serializer = self.serializer_class(data=data, many=False)
        if serializer.is_valid():
            return self._update_instance(key, **serializer.data)

        return handle_error('Validation failed.', status.HTTP_400_BAD_REQUEST)

    def _update_instance(self, key, **data):
        try:
            instance = self.service(key, user=self.request.user, **data)
            serializer = self.serializer_class(instance=instance, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectNotFoundError as error:
            return handle_error(error, status.HTTP_404_NOT_FOUND)
        except ValidationError as error:
            return handle_error(error, status.HTTP_400_BAD_REQUEST)
