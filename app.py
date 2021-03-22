import datetime
import pytz
from math import fabs
import logging

from flask import Flask, g, Response, request
from flask_cors import CORS, cross_origin
from db import get_db, query_db, upsert_db, page_db
from apscheduler.scheduler import Scheduler
#from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
# sched = BlockingScheduler()

import json
import atexit
from Crawl import main_job, print_job

from min_img import gei

from CONFIG import DEBUG

app = Flask(__name__)



# Create the logger and set the logging level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler
file_handler = logging.FileHandler('app_logs.log')

# Create formatter
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(message)s")

# Add formatter to the file handler
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)




@app.route('/')
def index():
    cur = get_db().cursor()
    pageDict = []
    for page in query_db('select * from pages'):
        dict1 = {}
        dict1 = {'page':page[0], 'category':page[1], 'lastindex': page[2]}
        pageDict.append(dict1)

    return Response(json.dumps(pageDict),  mimetype='application/json')


@app.route('/postpage', methods = ['GET', 'POST', 'DELETE'])
def postPage():
    if request.method == 'POST':
        try:
            page = request.form.get('page')
            category = request.form.get('category')
            
            insert_val = upsert_db(
                'INSERT INTO pages (page,category,lastindex) values(?,?,?)',
                (page, category, None)
            )
            if insert_val is True:
                return Response(json.dumps([{'success':True}]), mimetype='application/json')
            else:
                return Response(json.dumps([{'success':False}]), mimetype='application/json')
   
        except Exception as e: 
            return Response(json.dumps([{'success':False, 'Exception': str(e)}]), mimetype='application/json')

@app.route('/postpageapi', methods = ['GET', 'POST', 'DELETE'])
def postPageApi():
    if request.method == 'GET':
        try:
            pages = page_db()
            for i in pages:
                
                q = query_db("SELECT * FROM pages where page='%s'" % i['page_id'])
               
                if len(q) >= 1:
                    '''
                    q2 = query_db("SELECT * FROM pages where lastindex='%s'" % i['lastindex'])
                    
                    if len(q2) >= 1:
                        pass
                    else: 
                        
                        if(i['lastindex'] is None):
                            upsert_db("UPDATE pages SET lastindex=%s WHERE page='%s'" % (None, i['page_id']))
                        else:
                            upsert_db("UPDATE pages SET lastindex='%s' WHERE page='%s'" % (i['lastindex'],i['page_id']))
                    '''
                    pass
                else:
                    insert_val = upsert_db(
                        'INSERT INTO pages (page,category,lastindex,user) values(?,?,?,?)',
                        (i['page_id'], i['page_category'], None, i['user_id'])
                    )
            
            
            return Response(json.dumps([{'success':True}]), mimetype='application/json')
   
        except Exception as e: 
            return Response(json.dumps([{'success':False, 'Exception': str(e)}]), mimetype='application/json')

@app.route('/getevents', methods = ['GET', 'POST'])
@cross_origin()
def getAllEvents():
    if request.method == 'GET':
        try:
            eventList = []
            eId = request.args.get('eId')
            if eId is not None:
                for event in query_db("select * from events where id ='"+str(eId)+"'"):
                    dict1 =  {}
                    dict1 = {'id':event[0], 'page':event[1], 'title': event[2], 'description':event[3],'date':event[4], 'place':event[7], 'location':event[9], 'going':event[10], 'interested':event[11],'photo':event[12],'price':event[16],'type':event[21]}
                    eventList.append(dict1)
            else:
                for event in query_db('SELECT a.*, b.category, b.user from events a inner join pages b on a.page=b.page'):
                    dict1 =  {}
                    dict1 = {'id':event[0], 'page':event[1], 'title': event[2], 'description':event[3],'date':event[4], 'datefrom':event[5], 'dateto':event[6], 'place':event[7], 'location':event[9], 'going':event[10], 'interested':event[11],'photo':event[12], 'lat':event[13],'lon':event[14],'price':event[16],'city':event[17],'country':event[18],'state':event[19],'timezone':event[20],'type':event[21], 'user':event[22]}
                    eventList.append(dict1)
            return Response(json.dumps(eventList),  mimetype='application/json')
        except Exception as e: 
            return Response(json.dumps([{'success':False, 'Exception': str(e)}]), mimetype='application/json')   


@app.route('/redo', methods = ['GET', 'POST'])
def reload_db():
    logger.debug('Started the redo function')
    if request.method == 'GET':
        logger.debug('Got to GET the redo function')
        try:
            today = pytz.utc.localize(datetime.datetime.now())
            logger.debug('Got the time: '+str(today))
            eventList = []
            for event in query_db('SELECT a.*, b.category, b.user from events a inner join pages b on a.page=b.page'):
                dict1 =  {}

                # Converting the date to datetime obj
                date = event[6] if event[6] else event[4]
                print(date)
                date = date.replace(' ','')
                logger.debug('Got the date: '+str(date))
                if (date is not None) and (len(date) > 10):
                    logger.debug('Started condition date: '+date)

                    # Converting string to datetime
                    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                    time_distance = (date-today).days

                    logger.debug('Got a time difference: '+str(time_distance))

                    # only add events that are not yet finished or started in the last 30 days
                    if (time_distance > 0) or (fabs(time_distance) < 30):
                        logger.debug('{} {}: This time is added'.format(date, time_distance))
                        # dict1 = {'id':event[0], 'page':event[1], 'title': event[2],'date':event[4], 'datefrom':event[5], 'dateto':event[6], 'photo':event[12], 'city':event[17],'country':event[18],'state':event[19],'timezone':event[20],'type':event[21], 'user':event[22]}
                        eventList.append(event[0])
                        # eventList.append(dict1)

            return Response(json.dumps(eventList),  mimetype='application/json')
        except Exception as e:
            logger.exception(e)
            return Response(json.dumps([{'success':False, 'Exception': str(e)}]), mimetype='application/json')



redos = [209450986765684, 862736531139795, 3144988098936400, 137077944834086, 2940789689483198, 837239806849796, 1120952338341193, 326883501919730, 234541324918548, 592916348056639, 2531192603788836, 321623559228657, 447184343054004, 307599040230220, 336351167660644, 4153826711295673, 759961067984046, 1988433661297907, 270790871071944, 5271087176295713, 749037079384748, 462547271452710, 3921749577876683, 3512607348850581, 771383863491202, 480601683102641, 894071378093309, 145110577460008, 1929952800491253, 257774585853919, 716116859277581, 144654810769811, 424763428788591, 451581135927676, 415187772887398, 738152626902070, 471326357379541, 442042940349147, 892710814838610]
@app.route('/hd_img', methods = ['GET', 'POST'])
def hd_image_handler():
    logger.debug('Started the get hd images function')
    if request.method == 'GET':
        logger.debug('Got to GET the hd images function')
        try:
            for eid in redos:
                photo = gei(eid)
                event = query_db("SELECT photo from events WHERE id ='"+str(eid)+"'")[0][0]
                # Select the event from the db
                if photo is not None and (event.find('t1.0-0/cp0/e15/') != -1):
                    sql = f"UPDATE `events` SET photo={photo} WHERE id ='"+str(eid)+"'"
                    insert_val = upsert_db(sql)
                    # if insert_val == True:
                    print(eid, 'Inserted', insert_val)
                    logger.info(f"{eid} -->  'Inserted': {insert_val}")
            return Response(json.dumps(eventList),  mimetype='application/json')
        except Exception as e:
            logger.exception(e)
            return Response(json.dumps([{'success':False, 'Exception': str(e)}]), mimetype='application/json')




@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

count = 0
def sensor():
    global count
    sched.print_jobs()
    print('Count: ' , count)
    count += 1


# with app.app_context():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(func=main_job, trigger="interval", minutes=2)
#     scheduler.start()

# atexit.register(lambda: scheduler.shutdown())

@app.route('/start')
def starter():
    with app.app_context():
        print('Starting Job')
        main_job()

# with app.app_context():
#     print('Starting Job')
#     main_job()


# cron = Scheduler(daemon=True)
# cron.start()

# @cron.interval_schedule(hours=6)
# def job_function():
#     with app.app_context():
#         print('Starting Job')
#         main_job()

# @cron.interval_schedule(minutes=50)
# def print_function():
#     with app.app_context():
#         print('Starting Job')
#         print_job()

# atexit.register(lambda: cron.shutdown(wait=False))

# sched.start()

# @sched.scheduled_job('interval', minutes=2)
# def timed_job():
#     with app.app_context():
#         main_job()




if __name__ == "__main__":
    host = '127.0.0.1' if DEBUG else '0.0.0.0'
    app.run(threaded=True, host=host, port=80)
