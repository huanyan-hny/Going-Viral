from django.shortcuts import render
import toolbox
from django.http import HttpResponse
import executor
import logging

logger = logging.getLogger('django')


# Create your views here.
def submit(request):
    country = request.GET['country']
    population = request.GET['population']
    s = request.GET['s']
    i = request.GET['i']
    r = request.GET['r']
    d = request.GET['d']
    period = request.GET['period']
    start_date_raw = request.GET['date']

    session_id = request.GET['session_id']

    # Check population is valid
    if toolbox.check_int(population) is False:
        logger.info('Error: population ' + population + 'is not a number')
        return HttpResponse(content_type="application/json", status=406, content='population is not number')

    # Validate all rate percentages
    s_value = toolbox.try_parse_float(s)
    if s_value is False:
        logger.info('Error: s ' + s + 'is not a valid percentage')
        return HttpResponse(content_type="application/json", status=406, content='s is not number')
    elif s_value > 1.0 or s_value < 0.0:
        logger.info('Error: s ' + s_value + 'is out of range')
        return HttpResponse(content_type="application/json", status=406, content='s is out of range')

    i_value = toolbox.try_parse_float(i)
    if i_value is False:
        logger.info('Error: i ' + i + 'is not a valid percentage')
        return HttpResponse(content_type="application/json", status=406, content='i is not number')
    elif i_value > 1.0 or i < 0.0:
        logger.info('Error: i ' + i_value + 'is out of range')
        return HttpResponse(content_type="application/json", status=406, content='i is out of range')

    r_value = toolbox.try_parse_float(r)
    if r_value is False:
        logger.info('Error: r ' + r + 'is not a valid percentage')
        return HttpResponse(content_type="application/json", status=406, content='r is not number')
    elif r_value < 0.0 or r_value > 1.0:
        logger.info('Error: r ' + r_value + 'is out of range')
        return HttpResponse(content_type="application/json", status=406, content='r is out of range')

    d_value = toolbox.try_parse_float(d)
    if d_value is False:
        logger.info('Error: d ' + d + 'is not a valid percentage')
        return HttpResponse(content_type="application/json", status=406, content='d is not number')
    elif d_value > 1.0 or d_value < 0.0:
        logger.info('Error: d ' + d + 'is out of range')
        return HttpResponse(content_type="application/json", status=406, content='d is out of range')

    # Validate period
    if toolbox.check_int(period) is False:
        logger.info('Error: period ' + period + 'is not a number')
        return HttpResponse(content_type="application/json", status=406, content='period is not a number')
    period_value = int(period)
    if period_value > 365:
        logger.info('Error: period ' + period_value + 'out of range')
        return HttpResponse(content_type="application/json", status=406, content='period out of range')

    # Validate date offset
    if toolbox.check_int(start_date_raw) is False:
        logger.info('Error: date ' + start_date_raw + 'cannot be parsed')
        return HttpResponse(content_type="application/json", status=406, content='start date cannot be parsed')

    date_offset = int(start_date_raw)
    if date_offset > 13 or date_offset < 0:
        logger.info('Error: date ' + str(date_offset) + 'out of range')
        return HttpResponse(content_type="application/json", status=406, content='start date out of range')

        # Report
    logger.info('Ready to spread plague:')
    logger.info('Country: ' + country)
    logger.info('Population: ' + str(population))
    logger.info('Susceptible rate: ' + str(1.0))
    logger.info('Infection rate: ' + str(i))
    logger.info('Recover rate: ' + str(r))
    logger.info('Death rate: ' + str(d))
    logger.info('Period: ' + str(period))
    logger.info('Session id: ' + session_id)

    # Execute the command
    pid = executor.execute_job(session_id=session_id, country=country, population=int(population), s=1.0, r=float(r),
                               i=float(i), d=float(d),
                               period=period, date_offset=date_offset)
    logger.info('Execution started')
    return HttpResponse(content_type="application/json", status=200, content=pid)
