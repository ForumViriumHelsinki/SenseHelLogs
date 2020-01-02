from django.contrib import admin


class AdminSite(admin.AdminSite):
    site_header = 'SenseHel Logger Service Admin'
    site_title = 'SenseHel Logger Service Admin'
    site_url = None
