from django.contrib.admin.apps import AdminConfig


class AdminConfig(AdminConfig):
    default_site = 'sensehel_logs.admin_site.AdminSite'
