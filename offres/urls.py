from rest_framework.routers import DefaultRouter
from .views import OffreViewSet

router = DefaultRouter()
router.register(r'', OffreViewSet, basename='offres')  # '' = base path

urlpatterns = router.urls
