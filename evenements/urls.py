# evenements/urls.py
from rest_framework.routers import DefaultRouter
from .views_admin import EvenementAdminViewSet
from .views import EvenementViewSet

router = DefaultRouter()

# ADMIN D'ABORD (CRUCIAL)
router.register(
    r"admin",
    EvenementAdminViewSet,
    basename="admin-evenements"
)

# PUBLIC ENSUITE
router.register(
    r"",
    EvenementViewSet,
    basename="evenements"
)

urlpatterns = router.urls