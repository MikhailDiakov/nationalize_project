import requests
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Country, NameStat
from .serializers import NameStatSerializer, CountrySerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.db.models import F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class NameStatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="The name to analyze (e.g., 'John')",
            )
        ],
        responses=NameStatSerializer(many=True),
    )
    def get(self, request):
        name = request.query_params.get("name")
        if not name:
            return Response(
                {"error": "Missing name"}, status=status.HTTP_400_BAD_REQUEST
            )

        one_day_ago = now() - timedelta(days=1)

        stats = (
            NameStat.objects.filter(name=name, last_accessed_at__gte=one_day_ago)
            .select_related("country")
            .order_by("-probability")
        )

        if stats.exists():
            stats.update(count=F("count") + 1, last_accessed_at=now())
            serializer = NameStatSerializer(stats, many=True)
            return Response(serializer.data)

        nationalize_res = requests.get(
            "https://api.nationalize.io", params={"name": name}
        )
        if nationalize_res.status_code != 200:
            return Response(
                {"error": "Failed to get data from Nationalize"}, status=502
            )

        data = nationalize_res.json()
        countries_data = data.get("country", [])
        if not countries_data:
            return Response(
                {"error": "No countries found for this name"},
                status=status.HTTP_404_NOT_FOUND,
            )

        stats = []
        for item in countries_data:
            cca2 = item["country_id"]
            probability = item["probability"]

            country = Country.objects.filter(cca2=cca2).first()
            if not country:
                rest_res = requests.get(f"https://restcountries.com/v3.1/alpha/{cca2}")
                if rest_res.status_code != 200:
                    continue

                rest_data = rest_res.json()[0]
                country = Country.objects.create(
                    cca2=cca2,
                    name_common=rest_data["name"]["common"],
                    name_official=rest_data["name"]["official"],
                    region=rest_data.get("region", ""),
                    subregion=rest_data.get("subregion", ""),
                    independent=rest_data.get("independent", None),
                    google_maps=rest_data["maps"].get("googleMaps"),
                    open_street_maps=rest_data["maps"].get("openStreetMaps"),
                    capital=(
                        rest_data["capital"][0] if rest_data.get("capital") else None
                    ),
                    capital_lat=(
                        rest_data["capitalInfo"]["latlng"][0]
                        if rest_data.get("capitalInfo")
                        else None
                    ),
                    capital_lng=(
                        rest_data["capitalInfo"]["latlng"][1]
                        if rest_data.get("capitalInfo")
                        else None
                    ),
                    flag_png=rest_data["flags"].get("png"),
                    flag_svg=rest_data["flags"].get("svg"),
                    flag_alt=rest_data["flags"].get("alt"),
                    coat_of_arms_png=rest_data["coatOfArms"].get("png"),
                    coat_of_arms_svg=rest_data["coatOfArms"].get("svg"),
                    borders=",".join(rest_data.get("borders", [])),
                )

            stat = NameStat.objects.create(
                name=name,
                country=country,
                probability=probability,
                count=item.get("count", 1),
                last_accessed_at=now(),
            )
            stats.append(stat)

        serializer = NameStatSerializer(stats, many=True)
        return Response(serializer.data)


class PopularNamesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="country",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="2-letter country code (e.g., 'US')",
            )
        ],
        responses=CountrySerializer(many=True),
    )
    def get(self, request):
        country_code = request.query_params.get("country")
        if not country_code:
            return Response(
                {"error": "Missing country parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        name_counts = (
            NameStat.objects.filter(country__cca2=country_code)
            .values("name")
            .annotate(freq=Count("name"))
            .order_by("-freq")[:5]
        )

        if not name_counts:
            return Response(
                {"error": "No data found for the specified country"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(list(name_counts))
