import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(**kwargs):
        return User.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def get_token(api_client):
    def make_token(username="testusername", password="StrongPass123!321"):
        register_response = api_client.post(
            "/api/auth/register/",
            {
                "username": username,
                "password": password,
                "password_confirm": password,
            },
        )
        assert (
            register_response.status_code == 201 or register_response.status_code == 200
        ), register_response.data

        login_response = api_client.post(
            "/api/auth/login/",
            {
                "username": username,
                "password": password,
            },
        )
        assert login_response.status_code == 200, login_response.data
        return login_response.data["access"]

    return make_token


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


# ------------------------
# NameStatView Tests
# ------------------------


@pytest.mark.django_db
def test_namestat_unauthorized(api_client):
    response = api_client.get("/api/names/?name=John")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_namestat_missing_name(api_client, get_token):
    token = get_token()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get("/api/names/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@pytest.mark.django_db
@patch("core.views.requests.get")
def test_namestat_valid_name(mock_get, api_client, get_token):
    mock_get.side_effect = [
        MockResponse({"country": [{"country_id": "US", "probability": 0.85}]}, 200),
        MockResponse(
            [
                {
                    "name": {
                        "common": "United States",
                        "official": "United States of America",
                    },
                    "region": "Americas",
                    "subregion": "North America",
                    "independent": True,
                    "maps": {
                        "googleMaps": "https://maps.google.com",
                        "openStreetMaps": "https://osm.org",
                    },
                    "capital": ["Washington"],
                    "capitalInfo": {"latlng": [38.8951, -77.0364]},
                    "flags": {"png": "flag.png", "svg": "flag.svg", "alt": "US flag"},
                    "coatOfArms": {"png": "coa.png", "svg": "coa.svg"},
                    "borders": ["CAN", "MEX"],
                }
            ],
            200,
        ),
    ]

    token = get_token()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get("/api/names/?name=John")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert response.data[0]["name"] == "John"


# ------------------------
# PopularNamesView Tests
# ------------------------

from .models import (
    Country,
    NameStat,
)
from django.utils.timezone import now


@pytest.mark.django_db
def test_popular_names_unauthorized(api_client):
    response = api_client.get("/api/popular-names/?country=US")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_popular_names_valid(api_client, get_token):
    country = Country.objects.create(
        cca2="US", name_common="United States", name_official="United States of America"
    )
    for _ in range(3):
        NameStat.objects.create(
            name="John",
            country=country,
            count=1,
            probability=0.5,
            last_accessed_at=now(),
        )
    for _ in range(2):
        NameStat.objects.create(
            name="Mike",
            country=country,
            count=1,
            probability=0.3,
            last_accessed_at=now(),
        )

    token = get_token()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get("/api/popular-names/?country=US")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert response.data[0]["name"] == "John"
