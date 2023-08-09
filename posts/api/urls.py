from rest_framework.routers import SimpleRouter

from posts.api.views import PostViewSet

app_name = "posts"

router = SimpleRouter()
router.register("", PostViewSet)

urlpatterns = router.urls
