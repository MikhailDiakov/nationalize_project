from django.db import models


class Country(models.Model):
    cca2 = models.CharField(max_length=2, unique=True)
    name_common = models.CharField(max_length=128)
    name_official = models.CharField(max_length=256)
    region = models.CharField(max_length=128)
    subregion = models.CharField(max_length=128, null=True, blank=True)
    independent = models.BooleanField(null=True)
    google_maps = models.URLField(null=True, blank=True)
    open_street_maps = models.URLField(null=True, blank=True)
    capital = models.CharField(max_length=128, null=True, blank=True)
    capital_lat = models.FloatField(null=True, blank=True)
    capital_lng = models.FloatField(null=True, blank=True)
    flag_png = models.URLField(null=True, blank=True)
    flag_svg = models.URLField(null=True, blank=True)
    flag_alt = models.CharField(null=True, blank=True)
    coat_of_arms_png = models.URLField(null=True, blank=True)
    coat_of_arms_svg = models.URLField(null=True, blank=True)
    borders = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.cca2} - {self.name_common}"


class NameStat(models.Model):
    name = models.CharField(max_length=128)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    probability = models.FloatField()
    count = models.IntegerField(default=0)
    last_accessed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.country.cca2} ({self.probability})"
