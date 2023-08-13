from django.contrib.admin.apps import AdminConfig


class KapibaraAdminConfig(AdminConfig):
    default_site = "core_app.admin.KapibaraAdmin"
