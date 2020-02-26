import uuid
from rest_framework import serializers
from rest_framework.generics import CreateAPIView

from sensehel_logs_service import models
from .permissions import SenseHelAuthPermission
from .schema import fix_doc, expected_response_code
from .serializers import SubscriptionSerializer, ValueSerializer


class CreatedValueSerializer(ValueSerializer):
    attribute = serializers.IntegerField(source='attribute.attribute_id')

    class Meta(ValueSerializer.Meta):
        fields = ['attribute', 'timestamp', 'value']


class SubscriptionValuesSerializer(SubscriptionSerializer):
    values = serializers.SerializerMethodField()

    class Meta(SubscriptionSerializer.Meta):
        fields = ['uuid', 'values']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.values_data = kwargs.get('data', {}).get('values', {})
        self.values = []

    def create(self, validated_data):
        subscription = models.Subscription.objects.get(uuid=validated_data['uuid'])
        attrs_by_id = dict([(attr.attribute_id, attr) for attr in subscription.attributes.all()])
        for value in self.values_data:
            self.values.append(
                attrs_by_id[value['attribute']].values.create(value=value['value'], timestamp=value['timestamp']))
        return subscription

    def get_values(self, subscription):
        return CreatedValueSerializer(self.values, many=True).data

@fix_doc
@expected_response_code(201)
@SenseHelAuthPermission.append_doc
class SubmitData(CreateAPIView):
    """
    The SenseHel platform calls this API endpoint whenever new data is available for the subscription.
    Fields to be provided in the request body:

    - **uuid**: The UUID passed by SernseHel on subscription creation
    - **values**:
      - **attribute**: Attribute id passed by SernseHel on subscription creation; identifies the measured quantity
      - **timestamp**: Timestamp for when the value was measured
      - **value**: Numerical value
    """
    permission_classes = [SenseHelAuthPermission]
    queryset = models.Subscription.objects.all()
    serializer_class = SubscriptionValuesSerializer
    operation_id = 'Submit data'

    example_request = {
        'uuid': str(uuid.uuid4()),
        'values': [{
            'attribute': 1,
            'timestamp': '2020-02-26T12:29:05.059173Z',
            'value': 22.3
        }]
    }
    example_response = example_request
