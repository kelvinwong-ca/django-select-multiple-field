from django.contrib import admin

from .models import ChickenWings


class ChickenWingsAdmin(admin.ModelAdmin):
    model = ChickenWings
    list_display = ("__str__", "flavour")

    class Media:
        css = {
            "all": (
                "/static/multiselect-0.9.10/css/multi-select.css",
                "/static/css/style-multiselect.css",
            )
        }
        js = (
            "https://code.jquery.com/jquery-3.6.0.min.js",
            "/static/multiselect-0.9.10/js/jquery.multi-select.js",
            "/static/js/script-multiselect.js",
        )


admin.site.register(ChickenWings, ChickenWingsAdmin)
