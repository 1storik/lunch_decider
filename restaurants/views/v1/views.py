from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from datetime import date
from django.contrib.auth.models import User
from restaurants.models import Restaurant, Menu, Vote, Dish
from restaurants.serializers import RestaurantSerializer, MenuSerializer, DishSerializer, VoteSerializer, UserSerializer
from restaurants.views.v1.service import MenuService, DishService, VoteService


class RestaurantViewSetV1(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id:
            return Menu.objects.filter(restaurant__id=restaurant_id, date=date.today())
        return Menu.objects.filter(date=date.today())

    def perform_create(self, serializer):
        dish_ids = self.request.data.get('dish_ids', [])
        api_key = self.request.headers.get('x-api-key')
        result = MenuService.get_restaurant_and_dishes(dish_ids, api_key)
        if isinstance(result, Response):
            return result
        restaurant, dishes = result
        menu = serializer.save(restaurant=restaurant)
        menu.dishes.set(dishes)
        menu.save()


class CurrentDayMenuView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        menus = Menu.objects.filter(date=today)
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()


class CurrentDayResultsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        votes = Vote.objects.filter(menu__date=date.today()).values('menu__name').annotate(
            total_votes=Count('menu')).order_by('-total_votes')
        return Response(votes, status=status.HTTP_200_OK)


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        api_key = self.request.headers.get('x-api-key')
        restaurant = DishService.create_dishes(api_key)
        serializer.save(restaurant=restaurant)


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        menu_id = request.data.get('menu')

        menu = VoteService.create_vote(menu_id, user)

        return Response({"message": f"Voted for {menu.name} successfully."}, status=status.HTTP_201_CREATED)
