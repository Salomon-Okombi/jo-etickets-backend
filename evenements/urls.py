from rest_framework.routers import DefaultRouter
from .views import EvenementViewSet
from .views_admin import EvenementAdminViewSet

router = DefaultRouter()
router.register("evenements", EvenementViewSet, basename="evenements")
router.register("admin/evenements", EvenementAdminViewSet, basename="admin-evenements")

urlpatterns = router.urls