from django.db import models


class AuthenticationToken(models.Model):
    """
    Token used by SenseHel to authenticate subscription and data requests to this service.
    """
    token = models.UUIDField()

    def __str__(self):
        return self.token


class SensorAttribute(models.Model):
    """
    Represent one capability of a sensor, eg. temperature.
    """
    uri = models.CharField(max_length=255)
    description = models.CharField(max_length=128)

    def __str__(self):
        return self.description or self.uri


class Subscription(models.Model):
    uuid = models.UUIDField(editable=False, unique=True)

    def __str__(self):
        return f'Subscription({self.uuid})'


class AttributeSubscription(models.Model):
    subscription = models.ForeignKey(Subscription, related_name='attributes', on_delete=models.CASCADE)
    attribute_type = models.ForeignKey(SensorAttribute, related_name='subscriptions', on_delete=models.PROTECT)
    attribute_id = models.IntegerField(
        help_text='Id received from SenseHel, identifying a particular attribute of a particular sensor.')

    def __str__(self):
        return f'AttributeSubscription({self.id})'


class Value(models.Model):
    attribute = models.ForeignKey(AttributeSubscription, related_name='values', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=1)
    timestamp = models.DateTimeField()

    def __str__(self):
        return str(self.value)
