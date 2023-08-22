from rest_framework.routers import SimpleRouter

from posts.api.v1 import views

app_name = "posts"

router = SimpleRouter()
router.register("my", views.MyPostsViewSet, basename="my-posts")
router.register("", views.PostViewSet, basename="posts")

urlpatterns = router.urls
