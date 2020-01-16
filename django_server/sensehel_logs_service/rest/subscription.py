from rest_framework import viewsets, mixins, permissions, decorators
from rest_framework.response import Response

from sensehel_logs_service import models
from .permissions import SenseHelAuthPermission
from .serializers import SubscriptionSerializer


class CreateSubscriptionSerializer(SubscriptionSerializer):
    def create(self, validated_data):
        attributes = validated_data.pop('attributes', [])
        subscription = super().create(validated_data)
        for attr in attributes:
            attr_type = attr.pop('attribute_type')
            sensor_attr = models.SensorAttribute.objects.get_or_create(
                uri=attr_type['uri'], defaults={'description': attr_type['description']})[0]
            subscription.attributes.create(attribute_type=sensor_attr, **attr)
        return subscription


class SubscriptionsViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    serializer_classes = {'create': CreateSubscriptionSerializer}
    _permission_classes = {
        'create': [SenseHelAuthPermission],
        'unsubscribe': [SenseHelAuthPermission],
        'retrieve': [permissions.AllowAny]
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)

    @property
    def permission_classes(self):
        return self._permission_classes.get(self.action or 'create')

    @decorators.action(detail=False, methods=['POST'])
    def unsubscribe(self, request):
        try:
            models.Subscription.objects.get(uuid=request.data['uuid']).delete()
        except models.Subscription.DoesNotExist:
            return Response(status=404)
        return Response(status=204)
