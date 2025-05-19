from rest_framework import serializers
from .models import Country, NameStat


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class NameStatSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = NameStat
        fields = "__all__"
