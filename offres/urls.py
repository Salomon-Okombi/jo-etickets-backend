from rest_framework.routers import DefaultRouter
from .views import OffreViewSet
from .views_categories import CategorieOffreViewSet, CategorieOffreAdminViewSet

router = DefaultRouter()

# Catégories (public)
router.register(r"categories", CategorieOffreViewSet, basename="categories")

# Catégories (admin)
router.register(r"categories/admin", CategorieOffreAdminViewSet, basename="admin-categories")

# Offres
router.register(r"", OffreViewSet, basename="offres")

urlpatterns = router.urls