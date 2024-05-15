from rest_framework.routers import DefaultRouter
from familias.api.viewset import FamiliaViewSet


route_familia=DefaultRouter()


route_familia.register(
    prefix='familia',basename='familias',viewset=FamiliaViewSet
    
)