# billets/urls.py
from rest_framework.routers import DefaultRouter
from .views import EBilletViewSet

router = DefaultRouter()
router.register(r'', EBilletViewSet, basename='ebillets')

urlpatterns = router.urls
