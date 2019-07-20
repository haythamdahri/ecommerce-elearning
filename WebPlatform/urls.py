from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import handler404, handler500

import Ecommerce

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Ecommerce.urls')),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    # ---------------------- Paypal ----------------------
    path('paypal/', include('paypal.standard.ipn.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


