from rest_framework.routers import DefaultRouter
from users.api.views import UserApiViewSet

route_user=DefaultRouter()

route_user.register(
    prefix='users',basename='users',viewset=UserApiViewSet
)
