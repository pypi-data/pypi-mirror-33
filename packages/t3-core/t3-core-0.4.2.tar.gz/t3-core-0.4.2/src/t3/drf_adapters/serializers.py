from rest_framework import serializers


class ResourceSerializer(serializers.Serializer):
    resource_class = None

    def create(self, validated_data):
        assert self.resource_class is not None, '`resource_class` missing'
        resource = self.resource_class()
        return resource.create(**validated_data)

    def update(self, instance, validated_data):
        if self.partial:
            return instance.partial_update(**validated_data)
        return instance.update(**validated_data)

    def partial_update(self, instance, validated_data):
        return instance.partial_update(**validated_data)


class AccountSerializer(ResourceSerializer):
    id = serializers.UUIDField(read_only=True)
    phone = serializers.CharField()
    email = serializers.EmailField()
    name = serializers.CharField()
    points = serializers.IntegerField(read_only=True)
    meta = serializers.JSONField()
