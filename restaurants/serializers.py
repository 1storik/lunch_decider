from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Restaurant, Menu, Dish, Vote


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description']


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price']

    def create(self, validated_data):
        return Dish.objects.create(**validated_data)


class MenuSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)
    dish_ids = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.all(), many=True, write_only=True)

    class Meta:
        model = Menu
        fields = ['id', 'name', 'date', 'dishes', 'dish_ids']

    def create(self, validated_data):
        dishes = validated_data.pop('dish_ids')
        menu = Menu.objects.create(**validated_data)
        menu.dishes.set(dishes)
        return menu


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('Admin', 'Admin'), ('Employee', 'Employee')], write_only=True)
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'groups']

    def create(self, validated_data):
        role = validated_data.pop('role')

        user = User(**validated_data)
        user.set_password(validated_data['password'])

        if role == 'Admin':
            user.is_superuser = True
            user.is_staff = True

        user.save()
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        return user

    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['menu']


