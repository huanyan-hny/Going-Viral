from models import Airport, Airline, Country
import logging

logger = logging.getLogger('django')


def save_country(country):
    try:
        country.save()
        return True
    except Exception as e:
        logger.info('Error: cannot save Country, ' + str(country))
        logger.error(e.message)
        return False


def save_airport(airport):
    try:
        airport.save()
        return True
    except Exception as e:
        logger.error('Error: cannot save Airport, ' + str(airport))
        logger.error(e.message)
        return False


def save_airline(airline):
    try:
        airline.save()
        return True
    except Exception as e:
        logger.error('Error: cannot save Airline, ' + str(airline))
        logger.error(e.message)
        return False


def find_country_by_name(name):
    try:
        country = Country.objects.get(name=name)
        return country
    except Exception as e:
        logger.error('Error: cannot find area by name, ' + name)
        logger.error(e.message)
        return None


def find_airport_by_city(city_name):
    try:
        country = Airport.objects.get(city_name=city_name)
        return country
    except Exception as e:
        logger.error('Error: cannot find airport by city name, ' + city_name)
        logger.error(e.message)
        return None


def find_country_code_by_airport(airport_id):
    a = Airport.objects.get(pk=airport_id)
    return a.country.code


def generate_country_map():
    result = {}
    # For each country
    countries = Country.objects.all()
    for c in countries:
        content = {}
        content['code'] = c.code
        content['continent'] = ''
        content['label'] = c.name
        content['values'] = {
            "population": c.population,
            "i": 0,
            "s": c.population,
            "r": 0,
            "d": 0
        }
        result[c.code] = content
    all_map = {
        'countries': result,
        'day': 0
    }
    logger.debug(all_map)
    return all_map
