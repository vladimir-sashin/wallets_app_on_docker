from rest_framework.routers import DefaultRouter

from .views import ReportsViewSet, WalletViewSet

router = DefaultRouter()
router.register("wallets", WalletViewSet, basename="wallets")
router.register("reports", ReportsViewSet, basename="reports")

urlpatterns = []

urlpatterns += router.urls
