from api.views import CreateUserView, DeleteCypressTestUserView
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", health_check),
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
    path("api/v1/user/register/", CreateUserView.as_view(), name="register"),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            "api/v1/test_utils/__delete-cypress-test-user/",
            DeleteCypressTestUserView.as_view(),
            name="delete_cypress_test_user",
        ),
    ]
