from rest_framework.routers import DefaultRouter
from .views import EvenementViewSet
from .views_admin import EvenementAdminViewSet

router = DefaultRouter()

#  PUBLIC
# /api/evenements/
router.register(
    r"",
    EvenementViewSet,
    basename="evenements",
)

#  ADMIN
# /api/evenements/admin/
router.register(
    r"admin",
    EvenementAdminViewSet,
    basename="admin-evenements",
)

urlpatterns = router.urls