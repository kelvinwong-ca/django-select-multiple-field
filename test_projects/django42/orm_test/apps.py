from django.apps import AppConfig


class ORMTestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orm_test"
    verbose_name = "ORM Query Test"