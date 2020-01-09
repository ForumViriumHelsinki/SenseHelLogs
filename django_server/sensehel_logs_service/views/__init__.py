from django.conf.urls import url

from .permissions import SenseHelAuthPermission
from .subscription import CreateSubscription
from .data_submission import SubmitData


urls = [
    url('subscriptions/', CreateSubscription.as_view(), name='subscription-create'),
    url('values/', SubmitData.as_view(), name='values-create')
]
