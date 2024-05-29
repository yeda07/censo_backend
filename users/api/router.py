from rest_framework.routers import DefaultRouter
from users.api.views import UserApiViewSet,UserView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

route_user=DefaultRouter()

route_user.register(
    prefix='users',basename='users',viewset=UserApiViewSet
)

urlpatterns=[
    path('auth/me',UserView.as_view()),
    path('auth/login/',TokenObtainPairView.as_view(),name="TokenObtainPairView")    
]