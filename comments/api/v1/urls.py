from rest_framework.routers import SimpleRouter

from comments.api.v1 import views

app_name = "comments"

router = SimpleRouter()
router.register("", views.CommentViewSet, basename="comments")

urlpatterns = router.urls
