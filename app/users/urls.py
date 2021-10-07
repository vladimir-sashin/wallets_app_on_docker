from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CustomUserCreate

router = DefaultRouter()

# urlpatterns = [path("register/", CustomUserCreate.as_view(), name="register")]
router.register("register", CustomUserCreate, basename="register")

urlpatterns = []

urlpatterns += router.urls
