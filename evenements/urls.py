# evenements/urls.py
from rest_framework.routers import DefaultRouter
from .views import EvenementViewSet
from .views_admin import EvenementAdminViewSet

router = DefaultRouter()

# Public
router.register(r"", EvenementViewSet, basename="evenements")

# Admin
router.register(r"admin", EvenementAdminViewSet, basename="admin-evenements")

urlpatterns = router.urls