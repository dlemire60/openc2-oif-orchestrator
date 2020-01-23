from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from rest_framework.schemas import get_schema_view

from rest_framework_swagger.views import get_swagger_view

from . import views

admin.site.site_title = 'OpenC2 Orchestrator Administration'
admin.site.site_header = 'OpenC2 Orchestrator Admin'
admin.site.index_title = 'OpenC2 Orchestrator'

# Catch all URL
handler400 = views.bad_request
handler403 = views.permission_denied
handler404 = views.page_not_found
handler500 = views.server_error

api_patterns = [
    # Root Info
    path('', views.api_root, name='api.root'),

    # Account App
    path('account/', include('account.urls')),

    # Orchestrator App
    # path('orchestrator/', include('orchestrator.urls.api'), name='orchestrator.api_root'),

    # Schema
    path('schema/', include([
        path('', get_schema_view(title='OpenC2 Orchestrator API'), name='api.schema'),
        path('swagger/', get_swagger_view(title='OpenC2 Orchestrator API'), name='api.schema')
    ])),
]

gui_patterns = [
    # Account URLs - Needed for schema views by user permissions
    path('account/', include('django.contrib.auth.urls')),
]

if settings.ADMIN_GUI is True:
    # Admin GUI URLs
    gui_patterns.append(path('admin/', admin.site.urls))
else:
    # Admin GUI Redirect
    gui_patterns.append(path(r'admin/', views.gui_redirect))


urlpatterns = [
    # API Patterns
    path('api/', include(api_patterns), name='api'),

    # GUI Patterns
    path('', include(gui_patterns), name='gui')
]
