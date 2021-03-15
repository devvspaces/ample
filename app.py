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

app = Flask(__name__)

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

with app.app_context():
    print('Starting Job')
    main_job()


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
    app.run(threaded=True, host='0.0.0.0', port=80)