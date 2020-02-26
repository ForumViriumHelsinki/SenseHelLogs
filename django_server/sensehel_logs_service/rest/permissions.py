from rest_framework import permissions

from sensehel_logs_service import models


class SenseHelAuthPermission(permissions.BasePermission):
    """
    The SenseHel platform will authenticate the request by providing a previously exchanged
    **auth_token** in the request body.
    """
    def has_permission(self, request, view):
        token = request.data.get('auth_token', None)
        return token and models.AuthenticationToken.objects.filter(token=token).exists()

    @classmethod
    def append_doc(cls, fn):
        fn.__doc__ += '\n\n' + cls.__doc__
        return fn
