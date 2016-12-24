from django.contrib import admin

# Register your models here.
from models import *

admin.site.register(Country)
admin.site.register(Airport)
admin.site.register(Airline)