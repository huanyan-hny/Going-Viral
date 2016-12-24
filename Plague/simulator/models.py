from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    code = models.CharField(max_length=10, unique=True, db_index=True)
    population = models.IntegerField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return '(' + self.code + ')' + self.name

    def __unicode__(self):
        return u'{c}'.format(c=self.name)


class Airport(models.Model):
    city_name = models.CharField(max_length=200, unique=True, db_index=True)
    country = models.ForeignKey(Country, related_name='country')
    latitude = models.FloatField()
    longitude = models.FloatField()

    # 1 ~ 5
    airline_count=models.IntegerField(default=0)
    importance = models.IntegerField(default=1)

    def __str__(self):
        return self.city_name

    def __unicode__(self):
        return u'{c}'.format(c=self.city_name)


class Airline(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()

    # Date time fields
    departure_time = models.DateField()
    arrival_time = models.DateField()

    # Relative models
    from_airport = models.ForeignKey(Airport, related_name='from_airport', default=None)
    to_airport = models.ForeignKey(Airport, related_name='to_airport', default=None)

    # Importance
    importance = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'{c}'.format(c=self.name)


class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)
    infection_rate = models.FloatField()
    cure_rate = models.FloatField()
    susceptible_rate = models.FloatField()
    death_rate = models.FloatField()

    def __str__(self):
        return self.name
