from rest_framework import serializers

from tests.models import UserObject

class UserObjectSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    owner = serializers.UUIDField(required=False, read_only=True)

    class Meta:
        model = UserObject
        fields = '__all__'

    def create(self, validated_data):

        _object = UserObject.objects.create(**validated_data)
        return _object