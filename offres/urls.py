# offres/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OffreViewSet
from .views_categories import (
    CategorieOffreViewSet,
    CategorieOffreAdminViewSet,
)

router = DefaultRouter()

# Catégories (admin) — IMPORTANT : avant "categories"
router.register(
    r"categories/admin",
    CategorieOffreAdminViewSet,
    basename="offres-categories-admin",
)

# Catégories (public)
router.register(
    r"categories",
    CategorieOffreViewSet,
    basename="offres-categories",
)

# Offres
router.register(
    r"",
    OffreViewSet,
    basename="offres",
)

urlpatterns = [
    path("", include(router.urls)),
]