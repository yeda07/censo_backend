from rest_framework.routers import DefaultRouter
from multas.api.viewset import MultaViewSet


route_multa=DefaultRouter()


route_multa.register(
    prefix='multa',basename='multas',viewset=MultaViewSet
    
)