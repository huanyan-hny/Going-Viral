import threading
from subprocess import Popen
import logging

logger = logging.getLogger('django')


# Generate spark command line
def execute_job(session_id, country, population, s, i, r, d, period, date_offset):
    logger.info('Starting thread')
    cmd_list = ["spark-submit", "/home/hadoop/SparkLord/pycode/SIR_v7.py", str('plague-'+session_id), str(country), str(population), str(s), str(i), str(r), str(d),str(period), str(date_offset)]
    
    #with open('pycode/SIR_v6.py','r') as p:
    #    print p.readline() 

    #cmd_list=["spark-submit","/home/hadoop/SparkLord/pycode/SIR_v6.py"]
    logger.info("Generated commands: "+str(cmd_list))
    proc = Popen(cmd_list)
    logger.info('Submitted to spark with pid: ' + str(proc.pid))
    return proc.pid
