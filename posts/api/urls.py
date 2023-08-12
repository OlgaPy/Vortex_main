from rest_framework.routers import SimpleRouter

from posts.api import views

app_name = "posts"

router = SimpleRouter()
router.register("posts", views.PostViewSet, basename="posts")
router.register("my-posts", views.MyPostsViewSet, basename="my-posts")

urlpatterns = router.urls
