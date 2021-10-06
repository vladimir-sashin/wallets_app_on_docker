from rest_framework.routers import DefaultRouter

from .views import WalletViewSet

router = DefaultRouter()
router.register("wallets", WalletViewSet, basename="wallets")

urlpatterns = []

urlpatterns += router.urls
