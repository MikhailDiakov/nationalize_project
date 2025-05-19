import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_success(api_client):
    data = {
        "username": "testuser",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
    }
    response = api_client.post("/api/auth/register/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_register_passwords_do_not_match(api_client):
    data = {
        "username": "testuser2",
        "password": "StrongPass123!",
        "password_confirm": "NotMatching123!",
    }
    response = api_client.post("/api/auth/register/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password_confirm" in response.data


@pytest.mark.django_db
def test_register_missing_username(api_client):
    data = {
        "password": "SomePassword123!",
        "password_confirm": "SomePassword123!",
    }
    response = api_client.post("/api/auth/register/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data
