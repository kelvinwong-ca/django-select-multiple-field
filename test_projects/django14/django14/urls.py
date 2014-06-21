from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',  # NOQA

    url(r'^$', TemplateView.as_view(
        template_name='app/home.html'), name='home'),
    url(r'^pizzagigi/', include('pizzagigi.urls', namespace='pizza')),
    url(r'^forthewing/', include('forthewing.urls', namespace='ftw')),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
