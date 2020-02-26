import uuid
from rest_framework import viewsets, mixins, permissions, decorators
from rest_framework.response import Response

from sensehel_logs_service import models
from .permissions import SenseHelAuthPermission
from .schema import fix_doc, expected_response_code, override_example_request
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

    example_request = {
        'auth_token': str(uuid.uuid4()),
        'uuid': str(uuid.uuid4()),
        'attributes': [{
            'id': 1,
            'uri': 'http://urn.fi/URN:NBN:fi:au:ucum:r73',
            'description': 'temperature'
        }]
    }

    example_responses = {
        'create': {
            'uuid': example_request['uuid'],
            'attributes': [{
                'id': 1,
                'uri': 'http://urn.fi/URN:NBN:fi:au:ucum:r73',
                'description': 'temperature',
                'values': []
            }]
        },
        'retrieve': {
            'uuid': example_request['uuid'],
            'attributes': [{
                'id': 1,
                'uri': 'http://urn.fi/URN:NBN:fi:au:ucum:r73',
                'description': 'temperature',
                'values': [
                    {
                        'timestamp': '2020-02-26T12:29:05.059173Z',
                        'value': '22.5'
                    }
                ]
            }]
        },
        'unsubscribe': 'Empty response body'
    }

    @fix_doc
    @SenseHelAuthPermission.append_doc
    def create(self, request, *args, **kwargs):
        """
        Endpoint intended for the SenseHel platform to create a new subscription.
        Fields to be provided in the request body:

        - **uuid**: SenseHel should provide a sufficiently hard-to-guess uuid to allow anyone possessing it to
          access the reports generated for this subscription.
        - **attributes**: A list of attributes for which data will later be provided for the subscription.
          - **id**: Numeric id under which data will be reported
          - **uri**: URI formally specifying what quantity the attribute represents
          - **description**: Human readable representation of the quantity (e.g. humidity, temperature)

        Should return code 201 and the created subscription as JSON when successful.
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve subscription and attached data points. Note that this request does not require authentication,
        only knowledge of the subscription UUID. This endpoint is not called by SenseHel, only used by the service UI.
        Accepts optional **GET** parameter:

        - **values_timestamp_gt**: Filters values to include only those newer than the passed value.
        """
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)

    @property
    def permission_classes(self):
        return self._permission_classes.get(self.action or 'create')

    @expected_response_code(204)
    @SenseHelAuthPermission.append_doc
    @override_example_request({'uuid': example_request['uuid'], 'auth_token': example_request['auth_token']})
    @decorators.action(detail=False, methods=['POST'])
    def unsubscribe(self, request):
        """
        Delete the subscription and all related data points from the service.
        """
        try:
            models.Subscription.objects.get(uuid=request.data['uuid']).delete()
        except models.Subscription.DoesNotExist:
            return Response(status=404)
        return Response(status=204)
