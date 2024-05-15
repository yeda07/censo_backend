from rest_framework.routers import DefaultRouter
from actividades.api.viewset import ActividadViewSet


route_actividad=DefaultRouter()


route_actividad.register(
    prefix='actividad',basename='actividades',viewset= ActividadViewSet
    
)