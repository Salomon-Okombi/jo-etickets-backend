#urls analytic
from rest_framework.routers import DefaultRouter
from .views import StatistiquesVenteViewSet

router = DefaultRouter()
router.register(r'ventes', StatistiquesVenteViewSet, basename='statistiques-ventes')

urlpatterns = router.urls
