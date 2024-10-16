from restaurants.models import Restaurant, Dish, Menu, Vote
from rest_framework import serializers
from rest_framework.exceptions import APIException
from datetime import date


class CustomAPIException404(APIException):
    def __init__(self, detail):
        super(CustomAPIException404, self).__init__(detail)
        self.detail = detail

    status_code = 404
    default_detail = 'Invalid API Key.'
    default_code = 'invalid_api_key'


class MenuService:
    @staticmethod
    def get_restaurant_and_dishes(dish_ids, api_key):

        if api_key is None or api_key == '':
            raise serializers.ValidationError({"error": "x-api-key is required in header. "
                                                        "The API administrator can give it to you"})
        if not dish_ids or dish_ids == []:
            raise serializers.ValidationError({"error": "At least one dish is required."})
        try:
            restaurant = Restaurant.objects.get(api_key=api_key)
        except Restaurant.DoesNotExist:
            raise CustomAPIException404('Restaurant not found')

        dishes = Dish.objects.filter(id__in=dish_ids, restaurant=restaurant)
        if len(dishes) != len(dish_ids):
            raise serializers.ValidationError({"error": "One or more dishes do not belong to this restaurant."})

        return restaurant, dishes


class DishService:
    @staticmethod
    def create_dishes(api_key):
        if api_key is None or api_key == '':
            raise serializers.ValidationError({"error": "x-api-key is required in header. "
                                                        "The API administrator can give it to you"})
        try:
            restaurant = Restaurant.objects.get(api_key=api_key)
        except Restaurant.DoesNotExist:
            raise CustomAPIException404('Invalid API Key.')

        return restaurant


class VoteService:
    @staticmethod
    def create_vote(menu_id, user):
        if not menu_id:
            raise serializers.ValidationError({"error": "Menu ID is required."})

        try:
            menu = Menu.objects.get(id=menu_id, date=date.today())
        except Menu.DoesNotExist:
            raise CustomAPIException404("Menu not found or not available today.")

        if Vote.objects.filter(user=user, menu=menu).exists():
            raise serializers.ValidationError({"error": "You have already voted for this menu."})

        vote = Vote.objects.create(user=user, menu=menu)

        return menu
