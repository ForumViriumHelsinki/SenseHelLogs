import uuid

from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers
from rest_framework.test import APITestCase

from sensehel_logs_service import models


class SubscriptionTest(APITestCase):
    url = reverse('subscription-list')
    temp_uri = 'http://urn.fi/URN:NBN:fi:au:ucum:r73'

    subscription_fields = {
        'uuid': uuid.uuid4(),
        'attributes': [{
            'id': 1,
            'uri': temp_uri,
            'description': 'temperature'
        }]
    }

    def test_subscribe_not_authenticated(self):
        # When requesting to create a new subscription without providing an authentication token:
        response = self.client.post(self.url, dict(self.subscription_fields), format='json')

        # Then a 401 response is received:
        self.assertEqual(response.status_code, 401)

    def test_subscribe_bad_auth_key(self):
        # When requesting to create a new subscription, providing an invalid authentication token:
        response = self.client.post(self.url, dict(self.subscription_fields, auth_token=uuid.uuid4()), format='json')

        # Then a 401 response is received:
        self.assertEqual(response.status_code, 401)

    def test_subscribe(self):
        # When requesting to create a new subscription, providing a valid authentication token:
        token = models.AuthenticationToken.objects.create(token=uuid.uuid4())
        response = self.client.post(self.url, dict(self.subscription_fields, auth_token=token.token), format='json')

        # Then a 201 response is received:
        self.assertEqual(response.status_code, 201)
        uuid_ = str(self.subscription_fields['uuid'])
        self.assertDictEqual(response.data, {
            'uuid': uuid_,
            'attributes': [{
                'id': 1,
                'uri': self.temp_uri,
                'description': 'temperature',
                'values': []}]})

        # And a new subscription is created:
        subscription = models.Subscription.objects.get(uuid=uuid_)

        # And it has the appropriate attribute subscription:
        attr = subscription.attributes.get(attribute_id=1)

        # And the attribute subscription is linked to an automatically created attribute type
        self.assertEqual(attr.attribute_type.uri, self.temp_uri)

    def test_subscribe_to_existing_attribute_type(self):
        # Given that an attribute type has been created in the db:
        attr_type = models.SensorAttribute.objects.create(description='Temperature (degrees C)', uri=self.temp_uri)

        # When requesting to create a new subscription for an attribute of that type:
        token = models.AuthenticationToken.objects.create(token=uuid.uuid4())
        response = self.client.post(self.url, dict(self.subscription_fields, auth_token=token.token), format='json')

        # Then a 201 response is received:
        self.assertEqual(response.status_code, 201)

        # And a new subscription is created:
        subscription = models.Subscription.objects.get(uuid=self.subscription_fields['uuid'])

        # And it has the appropriate attribute subscription:
        attr = subscription.attributes.get(attribute_id=1)

        # And the attribute subscription is linked to the existing attribute type
        self.assertEqual(attr.attribute_type_id, attr_type.id)

    def test_fetch_subscription_data(self):
        # Given that there is a subscription for an attribute:
        subscription = models.Subscription.objects.create(uuid=self.subscription_fields['uuid'])
        attr = subscription.attributes.create(
            attribute_id=1,
            attribute_type=models.SensorAttribute.objects.create(
                description='temperature', uri=self.temp_uri))

        # And given that there are some values stored for the subscription:
        value = attr.values.create(timestamp = timezone.now(), value=22.5)

        # When requesting to fetch the subscription:
        response = self.client.get(reverse('subscription-detail', kwargs={'uuid': subscription.uuid}))

        # Then a 200 response is received:
        self.assertEqual(response.status_code, 200)

        # And it contains the subscription along with its attributes and their values:
        self.assertDictEqual(response.data, {
            'uuid': str(subscription.uuid),
            'attributes': [{
                'id': 1,
                'uri': 'http://urn.fi/URN:NBN:fi:au:ucum:r73',
                'description': 'temperature',
                'values': [{
                    'timestamp': serializers.DateTimeField().to_representation(value.timestamp),
                    'value': '22.5'
                }]
            }]
        })

    def test_unsubscribe(self):
        # Given that there is a subscription for an attribute:
        subscription = models.Subscription.objects.create(uuid=self.subscription_fields['uuid'])
        attr = subscription.attributes.create(
            attribute_id=1,
            attribute_type=models.SensorAttribute.objects.create(
                description='temperature', uri=self.temp_uri))

        # And given that there are some values stored for the subscription:
        value = attr.values.create(timestamp = timezone.now(), value=22.5)

        # When requesting to unsubscribe:
        token = models.AuthenticationToken.objects.create(token=uuid.uuid4())
        data = {'uuid': subscription.uuid, 'auth_token': token.token}
        response = self.client.post(reverse('subscription-unsubscribe'), data)

        # Then a 204 response is received:
        self.assertEqual(response.status_code, 204)

        # And the subscription is deleted from the db:
        self.assertEqual(0, models.Subscription.objects.count())
