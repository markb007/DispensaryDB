"""dispensarydb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from ajax_select import urls as ajax_select_urls
from django.views.static import serve

admin.autodiscover()

urlpatterns = [
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),
    path('', include('patientdb.urls')),
    path('', include('accounts.urls')),
    url(r'^select2/', include('django_select2.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [ 
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    """ urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT
        }),
    ] """

admin.site.index_title = "Welcome to DispensaryDB portal"
admin.site.site_title = "DispensaryDB"
admin.site.site_header = "DispensaryDB Administration"
