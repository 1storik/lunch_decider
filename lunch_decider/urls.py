"""
URL configuration for lunch_decider project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework import permissions
from rest_framework import routers

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from restaurants.views.v1.views import RestaurantViewSetV1, MenuViewSet, EmployeeViewSet, CurrentDayResultsViewSet, DishViewSet, \
    VoteViewSet, CurrentDayMenuView
from restaurants.views.v2.views import RestaurantViewSetV2

schema_view_v1 = get_schema_view(
    openapi.Info(
        title="Lunch Decider API",
        default_version='v1',
        description="API for lunch decision making - Version 1",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@lunchdecider.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

schema_view_v2 = get_schema_view(
    openapi.Info(
        title="Lunch Decider API",
        default_version='v2',
        description="API for lunch decision making - Version 2",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@lunchdecider.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

current_day_results = CurrentDayResultsViewSet.as_view({'get': 'list'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('swagger<format>/', schema_view_v1.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view_v1.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view_v1.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('swagger/v2<format>/', schema_view_v2.without_ui(cache_timeout=0), name='schema-json-v2'),
    path('swagger/v2/', schema_view_v2.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-v2'),

    path('results/current/', current_day_results, name='current_results'),
    path('menu/current_day/', CurrentDayMenuView.as_view(), name='current_day_menu'),
]

router_v1 = routers.DefaultRouter()
router_v2 = routers.DefaultRouter()
router_v1.register(r'api/v1/restaurants', RestaurantViewSetV1, basename='restaurants-v1')
router_v1.register(r'api/v1/menus', MenuViewSet, basename='menu-v1')
router_v1.register(r'api/v1/employees', EmployeeViewSet, basename='employee-v1')
router_v1.register(r'api/v1/dishes', DishViewSet)
router_v1.register(r'api/v1/votes', VoteViewSet)

router_v2.register(r'api/v2/restaurants', RestaurantViewSetV2, basename='menu-v2')
urlpatterns += router_v1.urls
urlpatterns += router_v2.urls
