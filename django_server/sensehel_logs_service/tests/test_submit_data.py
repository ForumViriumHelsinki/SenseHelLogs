import uuid
from collections import OrderedDict
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers
from rest_framework.test import APITestCase

from sensehel_logs_service import models


class SubmitDataTest(APITestCase):
    url = reverse('values-create')

    temp_uri = 'http://urn.fi/URN:NBN:fi:au:ucum:r73'
    timestamp = timezone.now()

    data_fields = {
        'uuid': uuid.uuid4(),
        'values': [{
            'attribute': 1,
            'timestamp': timestamp,
            'value': 22.3
        }]
    }

    def test_submit_data(self):
        # Given that there is a subscription for an attribute:
        subscription = models.Subscription.objects.create(uuid=self.data_fields['uuid'])
        attr = subscription.attributes.create(
            attribute_id=1,
            attribute_type=models.SensorAttribute.objects.create(
                description='temperature', uri=self.temp_uri))

        # When requesting to submit new data for the subscribed attribute:
        token = models.AuthenticationToken.objects.create(token=uuid.uuid4())
        response = self.client.post(self.url, dict(self.data_fields, auth_token=token.token), format='json')

        # Then a 201 response is received:
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.data, {
            'uuid': str(self.data_fields['uuid']),
            'values': [{
                'attribute': 1,
                'timestamp': serializers.DateTimeField().to_representation(self.timestamp),
                'value': '22.3'}]})

        # And new values are created for the subscription:
        self.assertEqual(attr.values.get().value, Decimal('22.3'))
