from rest_framework import permissions

from sensehel_logs_service import models


class SenseHelAuthPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        token = request.data.get('auth_token', None)
        return token and models.AuthenticationToken.objects.filter(token=token).exists()
