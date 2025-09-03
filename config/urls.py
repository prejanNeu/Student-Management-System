from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Smart Student Management API",
        default_version='v1',
        description="API documentation for Smart Student Management System",
        contact=openapi.Contact(email="unique69@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)





urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')), 
    path('', include('studentapp.urls')),
    path("", include("attendance.urls")),
    path("", include("assignment.urls")),
    path("",include("marksheet.urls")),
    # your app url
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
