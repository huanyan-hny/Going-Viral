from django.shortcuts import render
import dao
from models import Country, Airline, Airport
from django.http import HttpResponse, JsonResponse
import toolbox
import csv
from djqscsv import render_to_csv_response
import logging
import spark_connector as sc
import json
from django.db.models import Q
import pickle
import urllib2

logger = logging.getLogger('django')

'''
    CRUD actions
'''


# Country
def add_country(request):
    name = request.GET['name']
    population = request.GET['population']
    code = request.GET['code']
    if not population.isdigit():
        logger.info('Error: Population ' + population + ' is not an int')
        return HttpResponse(content_type="application/json", status=406, content='invalid population')

    # Create the area
    area = Country(name=name, population=int(population), code=code)
    if dao.save_country(area) is False:
        return HttpResponse(content_type="application/json", status=500, content='failed to save country')

    return HttpResponse(content_type="application/json", status=200)


# Add location to an existing country by name
def add_location_to_country(request):
    name = request.GET['name']

    # Input validation
    latitude_raw = toolbox.try_parse_float(request.GET['latitude'])
    if latitude_raw is False:
        logger.info('Error: Latitude ' + request.GET['latitude'] + ' is not a number')
        return HttpResponse(content_type="application/json", status=406, content='invalid latitude')
    elif latitude_raw > 90.0 or latitude_raw < -90.0:
        logger.info('Error: Latitude ' + latitude_raw + ' out of range -90~90')
        return HttpResponse(content_type="application/json", status=406, content='latitude out of range')

    longitude_raw = toolbox.try_parse_float(request.GET['longitude'])
    if longitude_raw is False:
        logger.info('Error: Longitude ' + request.GET['longitude'] + ' is not a number')
        return HttpResponse(content_type="application/json", status=406, content='invalid longitude')
    elif longitude_raw > 180.0 or longitude_raw < -180.0:
        logger.info('Error: Longitude ' + longitude_raw + ' out of range -180~180')
        return HttpResponse(content_type="application/json", status=406, content='longitude out of range')

    # Find the country first
    country = dao.find_country_by_name(name)
    if country is None:
        logger.info('Error: Cannot add location to country ' + name)
        return HttpResponse(content_type="application/json", status=406, content='cannot find country')

    # Add the location to the country
    country.update(latitude=float(latitude_raw), longitude=float(longitude_raw))
    return HttpResponse(content_type="application/json", status=200)


# Add an airport
def add_airport(request):
    city_name = request.GET['city_name']
    country_name = request.GET['country_name']
    latitude_raw = request.GET['latitude']
    longitude_raw = request.GET['longitude']

    # Input validation
    latitude = toolbox.try_parse_float(latitude_raw)
    if latitude is False:
        logger.info('Error: Latitude ' + request.GET['latitude'] + ' is not a number')
        return HttpResponse(content_type="application/json", status=406, content='invalid latitude')
    longitude = toolbox.try_parse_float(longitude_raw)
    if longitude is False:
        logger.info('Error: Longitude ' + request.GET['longitude'] + ' is not a number')
        return HttpResponse(content_type="application/json", status=406, content='invalid longitude')

    # Find country
    country = dao.find_country_by_name(country_name)
    if country is None:
        logger.info('Error: the country ' + country_name + ' of airport ' + city_name + ' cannot be found')
        return HttpResponse(content_type="application/json", status=406, content='cannot find country')

    # Add airport
    airport = Airport(city_name=city_name, country=country, latitude=latitude, longitude=longitude)
    if dao.save_airport(airport) is False:
        return HttpResponse(content_type="application/json", status=500, content='failed to save airport')

    return HttpResponse(content_type="application/json", status=200)


def update_airport_location(request):
    city_name = request.GET['city_name']
    latitude_raw = request.GET['latitude']
    longitude_raw = request.GET['longitude']

    # Input validation
    latitude = toolbox.try_parse_float(latitude_raw)
    if latitude is False:
        logger.info('Error: Latitude ' + request.GET['latitude'] + ' is not a number')
        return HttpResponse(content_type="application/json", status=406, content='invalid latitude')
    longitude = toolbox.try_parse_float(longitude_raw)
    if longitude is False:
        logger.info('Error: Longitude ' + request.GET['longitude'] + ' is not a number')
        return HttpResponse(content_type="application/json", status=406, content='invalid longitude')

    # Find airport
    try:
        Airport.objects.filter(city_name=city_name).update(latitude=latitude, longitude=longitude)
        return HttpResponse(content_type="application/json", status=200, content='updated ' + city_name)
    except Exception as e:
        logger.info("Error: cannot find airport " + city_name)
        return HttpResponse(content_type="application/json", status=406, content='city name not found')


# Airline
def add_airline(request):
    name = request.GET['name']
    departure = request.GET['departure_time']
    arrival = request.GET['arrival_time']
    from_city = request.GET['from_city']
    to_city = request.GET['to_city']
    capacity = request.GET['capacity']

    # Parse capacity number
    if toolbox.check_int(capacity) is False:
        logger.info('Error: Capacity ' + capacity + ' is not a number')
        return HttpResponse(content_type="application/json", status=406, content='invalid capacity')
    capacity_num = int(capacity)

    # Parse the date time
    departure_date = toolbox.try_parse_date(departure)
    arrival_date = toolbox.try_parse_date(arrival)
    if departure_date is None:
        logger.info('Error: departure_date ' + departure + ' is not valid')
        return HttpResponse(content_type="application/json", status=406, content='invalid departure_time')
    if arrival_date is None:
        logger.info('Error: arrival_date ' + arrival + ' is not valid')
        return HttpResponse(content_type="application/json", status=406, content='invalid arrival_time')

    # Find the airport by city
    from_airport = dao.find_airport_by_city(from_city)
    to_airport = dao.find_airport_by_city(to_city)
    if from_airport is None:
        logger.info('Error: the departure airport of city ' + from_city + ' cannot be found')
        return HttpResponse(content_type="application/json", status=406,
                            content='from_city cannot match to airport')
    if to_airport is None:
        logger.info('Error: the arrival airport of city ' + to_city + ' cannot be found')
        return HttpResponse(content_type="application/json", status=406, content='to_city cannot match to airport')

    # Create the airline
    airline = Airline(name=name, departure_time=departure_date, arrival_time=arrival_date, from_airport=from_airport,
                      to_airport=to_airport, capacity=capacity_num)
    if dao.save_airline(airline) is False:
        return HttpResponse(content_type="application/json", status_=500, content='failed to save airline')

    return HttpResponse(content_type="application/json", status=200)


def export_all_countries(request):
    queryset = Country.objects.values('code', 'name', 'population')
    return render_to_csv_response(queryset, delimiter=',')


def export_all_airlines(request):
    queryset = Airline.objects.values('name', 'capacity', 'departure_time', 'arrival_time',
                                      'from_airport__country__code',
                                      'to_airport__country__code')
    with open('airlines.csv', 'wb') as f:
        writer = csv.writer(f)
        for a in queryset.all():
            print a
            writer.writerow([a['name'], a['capacity'], toolbox.offset_date(a['departure_time']),
                             toolbox.offset_date(a['arrival_time']),
                             a['from_airport__country__code'],
                             a['to_airport__country__code']])
    return HttpResponse(content_type="application/json", status=200)


def init_job(request):
    logger.info('A new user comes in. Session key ' + request.session['SESSION_KEY'] + ' assigned')
    request.session['KAFKA_TOPIC'] = request.session['SESSION_KEY']


def init_country(request):
    logger.debug('Received request for init stage country info')
    all_map = dao.generate_country_map()

    # Store initial country info in session
    request.session['status'] = all_map

    # Output to file
    # with open('test_init.txt', 'wb') as t:
    #     json.dump(result, t)
    return JsonResponse(all_map['countries'])


def init_airports(request):
    logger.debug('Request for airport information')
    result = []

    airports = Airport.objects.values('city_name', 'longitude', 'latitude', 'importance', 'airline_count')
    logger.debug(type(airports))

    # # Count countries
    # countries={}
    # for a in airports:
    #     city_name=a['city_name']
    #     if city_name in countries.keys():
    #         countries[city_name]+=1
    #     else:
    #         countries[city_name]=1

    # Generate format
    for a in airports:
        content = {
            'city_name': a['city_name'],
            'longitude': a['longitude'],
            'latitude': a['latitude'],
            'airline_count': a['airline_count'],
            'importance': a['importance']
        }
        result.append(content)

    return JsonResponse(result, safe=False)


def update_countries(request):
    pass


def save_all_airlines(request):
    for i in range(1, 14, 1):
        target_url = "http://192.168.0.7:8080/sim/save_airlines?date_offset=" + str(i)
        try:
            response = urllib2.urlopen(target_url)
            if response.getcode() is not 200:
                logger.error('Error: status code of airline pickling is ' + response.getcode())
                logger.error(response)
            else:
                logger.info("Save date offset" + str(i))
        except Exception as e:
            logger.error('Error: http error ' + e.message)
            continue
    return HttpResponse(content_type="application/json", status=200, content='Saved')


def save_airlines(request):
    date_raw = request.GET["date_offset"]
    if toolbox.check_int(date_raw) is False:
        logger.info('Error: date ' + date_raw + 'cannot be parsed')
        return HttpResponse(content_type="application/json", status=406, content='date cannot be parsed')

    # Parse date offset
    date_offset = int(date_raw)
    target_date = toolbox.generate_date_from_offset(date_offset)
    logger.info("Target date is " + str(target_date))
    cities = {}
    airports = Airport.objects.all().values('pk', 'city_name', 'latitude', 'longitude', 'importance')
    for airport in airports:
        airlines = Airline.objects.filter(departure_time__day=target_date.day, from_airport__pk=airport['pk']).values(
            'to_airport__city_name',
            'to_airport__longitude',
            'to_airport__latitude',
            'to_airport__importance',
            'importance'
        )
        logger.info(
            'Target date ' + str(target_date) + ' has ' + str(airlines.count()) + ' airlines from city ' + airport[
                'city_name'])
        result = {
            'from': airport['city_name'],
            'latitude': airport['latitude'],
            'longitude': airport['longitude'],
            'importance': airport['importance'],
            'date': date_offset
        }
        airline_list = []
        for airline in airlines:
            content = {
                # 'target':airline['to_airport__city_name'],
                'longitude': airline['to_airport__longitude'],
                'latitude': airline['to_airport__latitude'],
                'importance': airline['importance']
            }
            airline_list.append(content)
        result['airlines'] = airline_list

        cities[airport['city_name']] = result

    logger.info(str(len(cities)) + ' airports complete')
    with open('storage/' + str(date_offset) + '.txt', 'wb') as s:
        pickle.dump(cities, s)
    return HttpResponse(content_type="application/json", status=200, content='Pickled')


def calculate_airport_airline_count(request):
    airports = Airport.objects.values('pk', 'city_name')
    stats = []
    for airport in airports:
        depart_airlines = Airline.objects.filter(from_airport__pk=airport['pk']).count()
        arrive_airlines = Airline.objects.filter(to_airport__pk=airport['pk']).count()
        logger.debug(
            'Airport ' + airport['city_name'] + ' depart: ' + str(depart_airlines) + ' arrive: ' + str(arrive_airlines))
        total = depart_airlines + arrive_airlines
        Airport.objects.filter(pk=airport['pk']).update(airline_count=total)
        logger.debug('Airport ' + airport['city_name'] + ' airline count: ' + str(total))
        stats.append(total)

    logger.debug("All stats collected.")
    stats.sort()
    logger.debug(stats)

    # Find pivot values
    length = len(stats)
    siz = length / 5
    logger.debug('1st pivot: ' + stats[length - siz])
    logger.debug('2nd pivot: ' + stats[length - 2 * siz])
    logger.debug('3rd pivot: ' + stats[length - 3 * siz])
    logger.debug('4th pivot: ' + stats[length - 4 * siz])


def calculate_airport_importance(request):
    airports = Airport.objects.values('pk', 'city_name', 'airline_count')
    for airport in airports:
        count = airport['airline_count']
        if count > 2000:
            Airport.objects.filter(pk=airport['pk']).update(importance=5)
        elif count > 750:
            Airport.objects.filter(pk=airport['pk']).update(importance=4)
        elif count > 200:
            Airport.objects.filter(pk=airport['pk']).update(importance=3)
        elif count > 20:
            Airport.objects.filter(pk=airport['pk']).update(importance=2)
        else:
            Airport.objects.filter(pk=airport['pk']).update(importance=1)
    logger.info('Airport importance are now updated')


def calculate_airline_importance(request):
    airlines = Airline.objects.values('pk', 'from_airport__importance', 'to_airport__importance')
    for airline in airlines:
        target_importance = airline['from_airport__importance'] + airline['to_airport__importance']
        Airline.objects.filter(pk=airline['pk']).update(importance=target_importance)
    logger.info("All airlines importance updated")


def update_kiev(request):
    k = Airport.objects.filter(city_name='Kiev')[0]
    airlines = Airline.objects.filter(Q(from_airport=k) | Q(to_airport=k)).values('pk', 'from_airport__importance',
                                                                                  'to_airport__importance')
    for airline in airlines:
        target_importance = airline['from_airport__importance'] + airline['to_airport__importance']
        logger.info(str(airline['from_airport__importance'] + "+" + str(airline['to_airport__importance'])))
        Airline.objects.filter(pk=airline['pk']).update(importance=target_importance)
    logger.info("All airlines for Kiev have their importance updated")


def export_kiev(request):
    k = Airport.objects.filter(city_name='Kiev')[0]
    result = []

    depart_from_k = Airline.objects.filter(from_airport=k).values('to_airport__latitude', 'to_airport__longitude',
                                                                  'importance')
    for d in depart_from_k:
        content = {
            'latitude': d['to_airport__latitude'],
            'longitude': d['to_airport__longitude'],
            'importance': d['importance']
        }
        result.append(content)
    logger.info("Depart from Kiev result length " + str(len(result)))

    arrive_at_k = Airline.objects.filter(to_airport=k).values('from_airport__latitude', 'from_airport__longitude',
                                                              'importance')
    for a in arrive_at_k:
        content = {
            'latitude': a['from_airport__latitude'],
            'longitude': a['from_airport__longitude'],
            'importance': a['importance']
        }
        result.append(content)
    logger.info("Arrive at Kiev result length " + str(len(result)))

    return JsonResponse({'from': 'Kiev', 'airlines': result})


'''
Spark related
'''


def start_kafka_consumer(request):
    logger.info('Starting kafka consumer')
    sc.start_consumer()
    logger.info('Long-live consumer thread is listening')
    return HttpResponse(content_type="application/json", status=200, content='Success')


def submit_job(request):
    country = request.GET['country']
    population = request.GET['population']
    s = request.GET['s']
    i = request.GET['i']
    r = request.GET['r']
    d = request.GET['d']
    period = request.GET['period']
    start_date_raw = request.GET['date']

    # Check session
    if not request.session.session_key:
        logger.error("Error: no session")
        return HttpResponse(content_type="application/json", status=400, content='no session')

    # Check country exists
    logger.info('Target country is ' + country)
    target_country = Country.objects.get(code=country)
    if target_country is None:
        logger.info("Error: Cannot find country with code " + country)
        return HttpResponse(content_type="application/json", status=406, content='unrecognized country code')

    # Check population is valid
    if toolbox.check_int(population) is False:
        print 'Error: population ', population, 'is not a number'
        return HttpResponse(content_type="application/json", status=406, content='population is not number')
    pop = int(population)
    if pop > target_country.population:
        logger.info('Error: Initially infected population ' + pop + ' exceeds current population ' + str(
            target_country.population))
        pop = target_country.population

    # Validate all rate percentages
    s_value = toolbox.try_parse_float(s)
    if s_value is False:
        print 'Error: s ', s, 'is not a valid percentage'
        return HttpResponse(content_type="application/json", status=406, content='s is not number')
    elif s_value > 1.0 or s_value < 0.0:
        print 'Error: s ', s_value, 'is out of range'
        return HttpResponse(content_type="application/json", status=406, content='s is out of range')

    i_value = toolbox.try_parse_float(i)
    if i_value is False:
        print 'Error: i ', i, 'is not a valid percentage'
        return HttpResponse(content_type="application/json", status=406, content='i is not number')
    elif i_value > 1.0 or i < 0.0:
        print 'Error: i ', i_value, 'is out of range'
        return HttpResponse(content_type="application/json", status=406, content='i is out of range')

    r_value = toolbox.try_parse_float(r)
    if r_value is False:
        print 'Error: r ', r, 'is not a valid percentage'
        return HttpResponse(content_type="application/json", status=406, content='r is not number')
    elif r_value < 0.0 or r_value > 1.0:
        print 'Error: r ', r_value, 'is out of range'
        return HttpResponse(content_type="application/json", status=406, content='r is out of range')

    d_value = toolbox.try_parse_float(d)
    if d_value is False:
        print 'Error: d ', d, 'is not a valid percentage'
        return HttpResponse(content_type="application/json", status=406, content='d is not number')
    elif d_value > 1.0 or d_value < 0.0:
        print 'Error: d ', d, 'is out of range'
        return HttpResponse(content_type="application/json", status=406, content='d is out of range')

    # Validate period
    if toolbox.check_int(period) is False:
        print 'Error: period ', period, 'is not a number'
        return HttpResponse(content_type="application/json", status=406, content='period is not a number')
    period_value = int(period)
    if period_value > 365:
        print 'Error: period ', period_value, 'out of range'
        return HttpResponse(content_type="application/json", status=406, content='period out of range')

    start_date = toolbox.try_read_date(start_date_raw)
    if start_date is False:
        print 'Error: date ', period_value, 'cannot be parsed'
        return HttpResponse(content_type="application/json", status=406, content='date cannot be parsed')

    # Report
    message = str(
        "Plague ready: country=" + country + ', population=' + str(
            pop) + ', s=' + s + ', i=' + i + ', r=' + r + ', d = ' + d + ', period = ' + period)
    logger.info(message)

    # Generate initial data
    all_map = dao.generate_country_map()
    request.session['status'] = all_map
    request.session['country_stats'] = {}

    # Store parameters in session
    request.session['country'] = country
    request.session['population'] = pop
    request.session['s'] = s
    request.session['i'] = i
    request.session['r'] = r
    request.session['d'] = d
    request.session['date'] = str(start_date)
    request.session['period'] = period

    # Validate session
    # if not request.session.session_key:
    #     request.session.save()
    # session_id = request.session.session_key
    # logger.info("The session id is " + str(session_id))

    # Execute the command
    # result = sc.submit_to_spark(session_id=request.session.session_key,
    #                             status=all_map,
    #                             country=country, population=pop,
    #                             s=1.0, r=float(r), i=float(i), d=float(d),
    #                             period=period, start_date=start_date)
    return HttpResponse(content_type="application/json", status=200, content='Success')
    # if result is True:
    #     logger.info('Successfully submitted spark job ')
    #     return HttpResponse(content_type="application/json", status=200, content='Success')
    # else:
    #     logger.error('Error: Spark submission failed')
    #     return HttpResponse(content_type="application/json", status=500,
    #                         content='Failed to create new spark job. Please contact the website administrator.')


def retrieve_status(request):
    logger.info('Received request for latest status')
    current_session = sc.get_session(request.session.session_key)
    logger.info("Current date " + str(current_session))

    return JsonResponse(current_session)


def export_stats(request):
    sc.persist_stats(request.session.session_key)
    return HttpResponse(content_type="application/json", status=200, content='persisted')


'''
    Retrieve update from the front
'''


def current_status(request):
    if not request.session.session_key:
        logger.error("Error: no session")
        return HttpResponse(content_type="application/json", status=400, content='no session')
    session_id = request.session.session_key
    status = sc.get_session(session_id)
    return JsonResponse(status['status'])


def current_stats(request):
    if not request.session.session_key:
        logger.error("Error: no session")
        return HttpResponse(content_type="application/json", status=400, content='no session')

    code = request.GET['code']
    session_id = request.session.session_key
    status = sc.get_session(session_id)
    if code not in status['country_stats'].keys():
        return JsonResponse("", safe=False)
    else:
        return JsonResponse(status['country_stats'][code])


'''
Test data
'''


def dummy_current_status(request):
    day_raw = request.GET['day']
    if toolbox.check_int(day_raw) is False:
        return HttpResponse(content_type="application/json", status=406, content='day is not a number')
    with open('storage/sample/' + str(day_raw) + '.txt') as d:
        content = json.load(d)
        return JsonResponse(content)


def dummy_current_stats(request):
    code = request.GET['code']
    with open('storage/sample/stats.txt') as d:
        content = json.load(d)
        country = content[code]
        return JsonResponse(country)


'''
Airline information
'''


def get_airlines(request):
    date_raw = request.GET['day']
    city_name = request.GET['city_name']

    # the_date = toolbox.try_read_date(date_raw)
    # if the_date is False:
    #     print 'Error: date ', date_raw, 'cannot be parsed'
    #     return HttpResponse(content_type="application/json", status=406, content='date cannot be parsed')

    if not toolbox.check_int(date_raw):
        print 'Error: date ', date_raw, 'cannot be parsed'
        return HttpResponse(content_type="application/json", status=406, content='day cannot be parsed')

    # Find the corresponding airline info the day matches to
    # logger.info('Received request for date ' + date_raw)
    # date_offset = toolbox.offset_date()
    # logger.info('Date difference: ' + str(date_offset))
    # date_mod = date_offset % 14
    # logger.info('Target date file is ' + str(date_mod))

    # Get the file
    target_date = int(date_raw) % 14
    date_base_path = 'storage/' + str(target_date) + '.txt'
    with open(date_base_path, 'rb') as s:
        content = pickle.load(s)
        # logger.info(content)
        target = content[city_name]
        return JsonResponse(target)
    return HttpResponse(content_type="application/json", status=500, content='Unknown reason, nothing to return')


def get_session(request):
    if not request.session.session_key:
        request.session.save()
    session_id = request.session.session_key
    return JsonResponse(session_id, safe=False)


def fuck_you(request):
    target_url = 'http://192.168.0.7:8080/sim/submit_plague?country=AF&population=1000&s=1&i=0.6&r=0.4&d=0.1&period=10&date=11%2F28%2F2016'
    response = urllib2.urlopen(target_url)
    if response.getcode is 200:
        return JsonResponse('Success', safe=False)
    else:
        return JsonResponse('Failed', safe=False)

'''
Now the work starts
'''
def atlas(request):
    return render(request, 'plague.html')