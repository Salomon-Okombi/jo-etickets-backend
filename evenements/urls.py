# evenements/urls.py
from rest_framework.routers import DefaultRouter
from .views import EvenementViewSet

router = DefaultRouter()
router.register(r'', EvenementViewSet, basename='evenements')  # <-- pas de préfixe

urlpatterns = router.urls
