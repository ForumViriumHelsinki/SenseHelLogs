from django.contrib import admin  # noqa
from django.db.models import Count, Min, Avg, Max

from . import models


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'attributes']
    search_fields = ['uuid']
    list_filter = ['attributes__attribute_type']

    def attributes(self, subscription):
        return list(models.SensorAttribute.objects\
            .filter(subscriptions__subscription=subscription)\
            .values_list('description', flat=True).distinct())


@admin.register(models.AttributeSubscription)
class AttributeSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'attribute_type', 'values', 'min', 'avg', 'max']
    list_filter = ['attribute_type']
    search_fields = ['subscription__uuid']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            values_count=Count('values'),
            min=Min('values__value'),
            avg=Avg('values__value'),
            max=Max('values__value')
        )

    def values(self, attr):
        return attr.values_count

    def min(self, attr):
        return '%s' % float('%.4g' % attr.min)

    def avg(self, attr):
        return '%s' % float('%.4g' % attr.avg)

    def max(self, attr):
        return '%s' % float('%.4g' % attr.max)


@admin.register(models.SensorAttribute)
class SensorAttributeAdmin(admin.ModelAdmin):
    list_display = ['description', 'uri', 'subscriptions_']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(subscriptions_=Count('subscriptions'))

    def subscriptions_(self, attr):
        return attr.subscriptions_


@admin.register(models.Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'timestamp')
    list_filter = ('attribute__attribute_type', )
    search_fields = ['attribute__subscription__uuid']
    date_hierarchy = 'timestamp'


@admin.register(models.AuthenticationToken)
class AuthenticationToken(admin.ModelAdmin):
    pass
