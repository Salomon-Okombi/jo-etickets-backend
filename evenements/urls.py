from rest_framework.routers import DefaultRouter
from .views import EvenementViewSet
from .views_admin import EvenementAdminViewSet

router = DefaultRouter()

#  PUBLIC
router.register(
    r"evenements",
    EvenementViewSet,
    basename="evenements",
)

# ADMIN
router.register(
    r"admin/evenements",
    EvenementAdminViewSet,
    basename="admin-evenements",
)

urlpatterns = router.urls