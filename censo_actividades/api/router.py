from rest_framework.routers import DefaultRouter
from censo_actividades.api.viewset import CensoActViewSet


route_censo_act=DefaultRouter()


route_censo_act.register(
    prefix='censo_actividad',basename='censo_actividades',viewset=CensoActViewSet
    
)