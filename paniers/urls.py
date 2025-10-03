# paniers/urls.py
from rest_framework.routers import DefaultRouter
from .views import PanierViewSet

router = DefaultRouter()
router.register(r'', PanierViewSet, basename='paniers')  # <-- vide ici

urlpatterns = router.urls
