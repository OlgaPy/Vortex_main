from rest_framework.routers import SimpleRouter

from users.api.v1 import views

app_name = "users"

router = SimpleRouter()
router.register("", views.UserViewSet, basename="users")

urlpatterns = router.urls
