import uuid

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from restaurants.models import Restaurant, Menu, Dish, Vote
from datetime import date

from restaurants.serializers import RestaurantSerializer, MenuSerializer


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(username, password, is_staff=False):
        return User.objects.create_user(username=username, password=password, is_staff=is_staff)
    return make_user


@pytest.fixture
def create_restaurant(db):
    def make_restaurant(name, description, api_key):
        restaurant = Restaurant.objects.create(name=name, description=description, api_key=api_key)
        return restaurant
    return make_restaurant


@pytest.mark.django_db
def test_create_restaurant(api_client, create_user):
    admin_user = create_user("admin", "password123", is_staff=True)
    api_client.force_authenticate(user=admin_user)

    url = reverse('restaurants-v1-list')
    data = {
        "name": "Test Restaurant",
        "description": "A test restaurant",
        "api_key": str(uuid.uuid4())
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Restaurant.objects.count() == 1
    assert Restaurant.objects.get().name == "Test Restaurant"


@pytest.mark.django_db
def test_vote_for_menu(api_client, create_user, create_restaurant):
    user = create_user("testuser", "password123")
    restaurant = create_restaurant("Test Restaurant", "A test restaurant", str(uuid.uuid4()))
    menu = Menu.objects.create(name="Test Menu", date=date.today(), restaurant=restaurant)

    api_client.force_authenticate(user=user)

    url = reverse('vote-list')  # This URL name should remain unchanged
    data = {"menu": menu.id}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Vote.objects.count() == 1
    assert Vote.objects.get().user == user
    assert Vote.objects.get().menu == menu


@pytest.mark.django_db
def test_get_current_day_results(api_client, create_user, create_restaurant):
    user1 = create_user("user1", "password123")
    user2 = create_user("user2", "password123")
    restaurant = create_restaurant("Test Restaurant", "A test restaurant", str(uuid.uuid4()))
    menu1 = Menu.objects.create(name="Menu 1", date=date.today(), restaurant=restaurant)
    menu2 = Menu.objects.create(name="Menu 2", date=date.today(), restaurant=restaurant)

    Vote.objects.create(user=user1, menu=menu1)
    Vote.objects.create(user=user2, menu=menu1)
    Vote.objects.create(user=user2, menu=menu2)

    api_client.force_authenticate(user=user1)

    url = reverse('current_results')  # Correct URL name
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['total_votes'] == 2
    assert response.data[1]['total_votes'] == 1


@pytest.mark.django_db
def test_create_employee(api_client, create_user):
    if not User.objects.filter(username="admin").exists():
        admin_user = create_user("admin", "password123", is_staff=True)
    api_client.force_authenticate(user=admin_user)

    url = reverse('employee-v1-list')
    data = {
        "username": "testemployee",
        "password": "password123",
        "role": "Employee"
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 2  # Теперь мы ожидаем 2 пользователя: admin и testemployee
    assert User.objects.get(username="testemployee").groups.filter(name="Employee").exists()


@pytest.mark.django_db
def test_create_admin(api_client, create_user):
    admin_user = create_user("admin", "password123", is_staff=True)
    api_client.force_authenticate(user=admin_user)

    url = reverse('employee-v1-list')
    data = {
        "username": "testadmin",
        "password": "password123",
        "role": "Admin"
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED

    assert User.objects.count() == 2

    user = User.objects.get(username="testadmin")
    assert user.groups.filter(name="Admin").exists()
    assert user.is_superuser
    assert user.is_staff


@pytest.mark.django_db
def test_restaurant_serializer():
    # Создание ресторана для тестирования
    restaurant = Restaurant.objects.create(name="Test Restaurant", description="A test restaurant")

    serializer = RestaurantSerializer(instance=restaurant)

    assert serializer.data == {
        'id': restaurant.id,
        'name': restaurant.name,
        'description': restaurant.description
    }


@pytest.mark.django_db
def test_menu_serializer():
    restaurant = Restaurant.objects.create(name="Test Restaurant", description="A test restaurant")
    dish1 = Dish.objects.create(name="Dish 1", description="Test Dish 1", price=10.00, restaurant=restaurant)
    dish2 = Dish.objects.create(name="Dish 2", description="Test Dish 2", price=15.00, restaurant=restaurant)

    menu_data = {
        'name': 'Test Menu',
        'date': '2024-10-15',
        'dish_ids': [dish1.id, dish2.id]
    }

    serializer = MenuSerializer(data=menu_data)
    assert serializer.is_valid()

    menu = serializer.save(restaurant=restaurant)
    assert menu.name == menu_data['name']
    assert str(menu.date) == menu_data['date']
    assert set(menu.dishes.values_list('id', flat=True)) == {dish1.id, dish2.id}
