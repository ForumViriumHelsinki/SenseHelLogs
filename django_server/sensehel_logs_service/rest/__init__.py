from django.conf.urls import url
from rest_framework import routers

from .permissions import SenseHelAuthPermission  # noqa
from .subscription import SubscriptionsViewSet
from .data_submission import SubmitData
from .schema import APISchema
from .schema_view import schema_view

router = routers.DefaultRouter()
router.register('subscriptions', SubscriptionsViewSet)

urls = router.urls + [
    url('values/', SubmitData.as_view(), name='values-create')
]
