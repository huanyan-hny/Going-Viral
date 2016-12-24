import logging
import toolbox
import urllib2
from kafka import KafkaClient, KafkaConsumer
import json
from models import Country

# Submit job to spark and get updates
sessions = {}
logger = logging.getLogger('django')

# Store a country name map
all_countries = Country.objects.values('code', 'name')
country_names = {}
for entry in all_countries:
    country_names[entry['code']] = entry['name']
logger.info('Generated country name map of ' + str(len(country_names)) + ' countries')


def start_consumer():
    consumer = KafkaConsumer(bootstrap_servers=['54.89.85.133:9092'], group_id=None,
                             auto_offset_reset='latest')
    consumer.subscribe(pattern='^plague-.*')
    # consumer.subscribe(pattern='^world')

    # Only print the first a few characters of a message of the screen is not messed
    for message in consumer:
        try:
            topic = message.topic
            # Find the session by id
            # session_id = topic[7:]
            # session_id = 'world'
            # logger.info('Session id: ' + session_id)
            v = message.value
            logger.info('Topic: ' + topic)
            try:
                value = v.decode('utf-8')
                logger.info('Message: ' + value)
            except UnicodeDecodeError:
                logger.info('Cannot decode: ' + v)
                continue
            #
            # # Locate the session from map
            # if not session_id in sessions.keys():
            #     logger.error("Error: session " + session_id + " cannot be retrieved")
            #     continue

            # Update session
            # update_session(session_id=session_id, session=sessions[session_id], value=value)
            new_update_session(value)
            logger.info("Session updated")
        except Exception as e:
            logging.exception('Exception during processing kafka messages:')
            continue


def report_session(session):
    logger.debug("Report session:")
    logger.debug(str(session))


def persist_stats(session_id):
    session = sessions[session_id]
    stats = session['country_stats']
    with toolbox.safe_open_w('storage/' + str(session_id) + "/" + "stats.txt") as s:
        json.dump(stats, s)


def new_update_session(value):
    try:
        content = json.loads(value)
    except Exception:
        logger.info("Cannot convert " + str(value) + " from json")
        return

    session_id = content['topic']
    topic = session_id[7:]
    logger.info('Got topic ' + str(topic))
    if topic not in sessions:
        logger.info('Error: session_id ' + str(session_id) + ' cannot be found')
        return

    session = sessions[topic]

    date = content['day']
    countries = content['population']
    logger.info("Updating info day " + str(date))
    session['day'] = date

    # session
    country_map = {}
    country_stats = session['country_stats']

    for country in countries.keys():
        # Update status map
        in_country = countries[country]
        content = {
            'code': country,
            'values': {
                's': in_country['S'],
                'i': in_country['I'],
                'r': in_country['R'],
                'd': in_country['D'],
                'population': int(in_country['S']) + int(in_country['I']) + int(in_country['R']) + int(in_country['D'])
            },
            'continent': "",
            'label': country_names[country]
        }
        country_map[country] = content

        # Update stats map
        if not country in country_stats.keys():
            stat_map = {
                's': [in_country['S']],
                'i': [in_country['I']],
                'r': [in_country['R']],
                'd': [in_country['D']]
            }
            country_stats[country] = stat_map
        else:
            stat_map = country_stats[country]
            stat_map['s'].append(in_country['S'])
            stat_map['i'].append(in_country['I'])
            stat_map['r'].append(in_country['R'])
            stat_map['d'].append(in_country['D'])

    all_map = {
        'day': date,
        'countries': country_map
    }
    logger.info("Updating the session with new status: ")
    # logger.info(all_map)

    # Update the session
    session['status'] = all_map
    logger.info('Status stored')

    # Export to file
    with toolbox.safe_open_w('storage/' + str(session_id) + "/" + str(date) + ".txt") as s:
        json.dump(all_map, s)
    logger.info('Persisted to file')


def update_session(session_id, session, value):
    content = json.loads(value)

    date = content['day']
    countries = content['population']
    logger.info("Updating info day " + str(date))
    session['day'] = date

    # session
    country_map = {}
    country_stats = session['country_stats']

    for country in countries.keys():
        # Update status map
        in_country = countries[country]
        content = {
            'code': country,
            'values': {
                's': in_country['S'],
                'i': in_country['I'],
                'r': in_country['R'],
                'd': in_country['D'],
                'population': int(in_country['S']) + int(in_country['I']) + int(in_country['R']) + int(in_country['D'])
            },
            'continent': "",
            'label': country_names[country]
        }
        country_map[country] = content

        # Update stats map
        if not country in country_stats.keys():
            stat_map = {
                's': [in_country['S']],
                'i': [in_country['I']],
                'r': [in_country['R']],
                'd': [in_country['D']]
            }
            country_stats[country] = stat_map
        else:
            stat_map = country_stats[country]
            stat_map['s'].append(in_country['S'])
            stat_map['i'].append(in_country['I'])
            stat_map['r'].append(in_country['R'])
            stat_map['d'].append(in_country['D'])

    all_map = {
        'day': date,
        'countries': country_map
    }
    logger.info("Updating the session with new status: ")
    # logger.info(all_map)

    # Update the session
    session['status'] = all_map
    logger.info('Status stored')

    # Export to file
    with toolbox.safe_open_w('storage/' + str(session_id) + "/" + str(date) + ".txt") as s:
        json.dump(all_map, s)
    logger.info('Persisted to file')


def submit_to_spark(session_id, status, country, population, s, r, i, d, period, start_date):
    # Report knowledge on the session
    if session_id in sessions.keys():
        logger.info("One recorded spark job is already there: ")
        # logger.info(str(sessions[session_id]))
    else:
        logger.info("New spark job to submit for session " + session_id)

    # Keep in the management
    sessions[session_id] = {
        'day': 0,
        'status': status,
        'country_stats': {}
    }

    # generate the url
    spark_lord = "http://52.23.238.38/listener/submit-job?"
    spark_lord += 'session_id=' + session_id
    spark_lord += '&country=' + country
    spark_lord += '&population=' + str(population)
    spark_lord += '&s=' + str(s)
    spark_lord += '&i=' + str(i)
    spark_lord += '&r=' + str(r)
    spark_lord += '&d=' + str(d)
    spark_lord += '&period=' + str(period)

    date_offset = toolbox.offset_date(start_date)
    date_offset = date_offset % 14
    logger.info('Date offset is ' + str(date_offset))

    spark_lord += '&date=' + str(date_offset)
    logger.info('Target Url: ' + spark_lord)

    # Send http request
    try:
        response = urllib2.urlopen(spark_lord)
        if response.getcode() is not 200:
            logger.error('Error: status code of spark job submission is ' + response.getcode())
            logger.error(response)
            return False
        else:
            logger.info("Submission to spark got 200")
            return True
    except Exception as e:
        logger.error('Error: http error ' + e.message)
        return False


def get_session(session_id):
    if session_id not in sessions.keys():
        logger.error('Requesting for untracked session ' + str(session_id))
        return {
            'day': 0,
            'status': {},
            'country_stats': {}
        }
    else:
        logger.info("Tracking session " + session_id)
        return sessions[session_id]
