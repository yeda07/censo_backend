from rest_framework.routers import DefaultRouter
from personas.api.viewset import PersonaViewSet


route_persona=DefaultRouter()


route_persona.register(
    prefix='persona',basename='personas',viewset=PersonaViewSet
    
)