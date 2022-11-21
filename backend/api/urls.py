from django.urls import include, path, re_path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

# from .views import CustomUserCreateView, UserApiView
from backend.api.views import FollowViewSet

router = DefaultRouter()
# router.register(
#     r'users\/(?P<user_id>\d+)\/subscribe\/', FollowViewSet, basename='follows')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
