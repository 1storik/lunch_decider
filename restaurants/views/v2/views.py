from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from restaurants.models import Restaurant
from restaurants.serializers import RestaurantSerializer
from drf_yasg.utils import swagger_auto_schema


class RestaurantViewSetV2(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(tags=['v2'])
    def list(self, request, *args, **kwargs):
        app_version = request.app_version
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response_data = [
            {
                **restaurant_data,
                'menu_count': restaurant.menus.count(),
                'additional_info': "New feature for version 2.0" if app_version == '2.0' else "You have version 1.0"
            }
            for restaurant_data, restaurant in zip(serializer.data, queryset)
        ]

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['v2'])
    def perform_create(self, serializer):
        serializer.save()


