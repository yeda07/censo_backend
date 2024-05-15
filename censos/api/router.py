from rest_framework.routers import DefaultRouter
from censos.api.viewset import CensoViewSet


route_censo=DefaultRouter()


route_censo.register(
    prefix='censo',basename='censos',viewset=CensoViewSet
    
)