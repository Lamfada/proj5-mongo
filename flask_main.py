"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates: 
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will 
   - User input/output is in local (to the server) time.  
"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import url_for
from flask import jsonify # For AJAX transactions

import json
from bson import ObjectId
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we may still need time
from dateutil import tz  # For interpreting local times

# Mongo database
from pymongo import MongoClient
import pymongo

###
# Globals
###
import CONFIG

app = flask.Flask(__name__)

try: 
    dbclient = MongoClient(CONFIG.MONGO_URI)
    db = dbclient.get_default_database( )
    collection = db['dated']

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)

import uuid
app.secret_key = str(uuid.uuid4())

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Main page entry")
  flask.session['memos'] = get_memos()
  for memo in flask.session['memos']:
      app.logger.debug("Memo: " + str(memo))
  return flask.render_template('index.html')



@app.route("/create")
def create():
    app.logger.debug("Create")
    return flask.render_template('create.html')

#enter memo into database
@app.route("/_enter")
def enter():
    """
    Function to enter a user's dated memo into the database, or at least tell them
    that we tried and failed.
    """
    date = request.args.get("date",type = str)
    memo = request.args.get("memo",type = str)
    mess = "Success"
    try:
         time = arrow.get(date, 'YYYY-MM-DD HH:mm').to('local').isoformat()
         record = {"type":"dated_memo","date":time,"text":memo}
         collection.insert(record)
    except:
        #Tell User that for some reason the server failed to store their memo.
        mess = "Failure"
        rsult = {"message":mess}
    return jsonify(result=rsult)

@app.route("/_rem")
def remove():
    """
    Remove an entry from the database.
    """
    print("Begin")
    id = request.args.get("id",type=str)
    id = ObjectId(id)
    collection.delete_one({'_id':id})
    return jsonify(result={"why":"not"})

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#################
#
# Functions used within the templates
#
#################

# NOT TESTED with this application; may need revision 
#@app.template_filter( 'fmtdate' )
# def format_arrow_date( date ):
#     try: 
#         normal = arrow.get( date )
#         return normal.to('local').format("ddd MM/DD/YYYY")
#     except:
#         return "(bad date)"


@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case. 
    """
    try:
        then = arrow.get(date).to('local')
        then_past = then.replace(days=-1)
        then_future = then.replace(days=1)
        now = arrow.utcnow().to('local')
        now = now.replace(days=-1)
        #I know it looks weird to take a day off of now, but for some reason it seems
        # to be generating tomorrow when asked for now. The replacement is
        # correcting for that strange behavior.
        if then.date() == now.date():
            human = "Today"
        else: 
            human = then.humanize(now)
            if then_past.date() == now.date():
                human = "Tomorrow"
            if then_future.date() == now.date():
                human = "Yesterday"
            if human == "in a day":
                human = "Tomorrow"
    except: 
        human = date
    return human

#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
    Returns all memos in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    for record in collection.find( { "type": "dated_memo" } ).sort('date',pymongo.ASCENDING):
        record['date'] = arrow.get(record['date']).isoformat()
        print (type(record['_id']))
        record['_id'] = str(record['_id'])
        records.append(record)
    return records 


if __name__ == "__main__":
    # App is created above so that it will
    # exist whether this is 'main' or not
    # (e.g., if we are running in a CGI script)
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    # We run on localhost only if debugging,
    # otherwise accessible to world
    if CONFIG.DEBUG:
        # Reachable only from the same computer
        app.run(port=CONFIG.PORT)
    else:
        # Reachable from anywhere 
        app.run(port=CONFIG.PORT,host="0.0.0.0")

    
