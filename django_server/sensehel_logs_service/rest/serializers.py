from rest_framework import serializers

from sensehel_logs_service import models


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Value
        fields = ['timestamp', 'value']


class AttributeSubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='attribute_id')
    uri = serializers.CharField(source='attribute_type.uri')
    description = serializers.CharField(source='attribute_type.description')
    values = serializers.SerializerMethodField()

    class Meta:
        model = models.AttributeSubscription
        fields = ['id', 'uri', 'description', 'values']

    def get_values(self, attribute_subscription):
        from_timestamp = self.context['request'].GET.get('values_timestamp_gt', None)
        if from_timestamp:
            qs = attribute_subscription.values.filter(timestamp__gt=from_timestamp)
        else:
            qs = attribute_subscription.values.all()
        return ValueSerializer(qs, many=True).data


class SubscriptionSerializer(serializers.ModelSerializer):
    attributes = AttributeSubscriptionSerializer(many=True)
    uuid = serializers.CharField()

    class Meta:
        model = models.Subscription
        fields = ['uuid', 'attributes']
