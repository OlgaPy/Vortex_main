from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from two_factor.urls import urlpatterns as tf_urls

v1_urls = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="v1-api:schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="v1-api:schema"),
        name="redoc",
    ),
    path("", include("posts.api.urls", namespace="posts")),
    path("", include("users.api.urls", namespace="users")),
]

urlpatterns = [
    path("", include(tf_urls)),
    path(f"{settings.DJANGO_ADMIN_PATH}/", admin.site.urls),
    path("api/v1/", include((v1_urls, "v1"), namespace="v1-api")),
]
