from rest_framework import serializers
from rest_framework.generics import CreateAPIView

from sensehel_logs_service import models
from .permissions import SenseHelAuthPermission


class AttributeSubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='attribute_id')
    uri = serializers.CharField(source='attribute_type.uri')
    description = serializers.CharField(source='attribute_type.description')

    class Meta:
        model = models.AttributeSubscription
        fields = ['id', 'uri', 'description']


class SubscriptionSerializer(serializers.ModelSerializer):
    attributes = AttributeSubscriptionSerializer(many=True)
    uuid = serializers.CharField()

    class Meta:
        model = models.Subscription
        fields = ['uuid', 'attributes']

    def create(self, validated_data):
        attributes = validated_data.pop('attributes', [])
        subscription = super().create(validated_data)
        for attr in attributes:
            attr_type = attr.pop('attribute_type')
            sensor_attr = models.SensorAttribute.objects.get_or_create(
                uri=attr_type['uri'], defaults={'description': attr_type['description']})[0]
            subscription.attributes.create(attribute_type=sensor_attr, **attr)
        return subscription


class CreateSubscription(CreateAPIView):
    permission_classes = [SenseHelAuthPermission]
    queryset = models.Subscription.objects.all()
    serializer_class = SubscriptionSerializer
