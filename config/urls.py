from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "UGHE Test Web App - Content Admin"
admin.site.site_title = "UGHE Test Web App"
admin.site.index_title = "Manage the homepage content"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("cms.urls")),
]

# Serve uploaded media (slides, logo) in development / Docker setup
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
