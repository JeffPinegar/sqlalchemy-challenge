# Jeff Pinegar
# jeffpinegar1@gmail.com
# Dec. 7, 2022

# To run this in git bash 
    # export FLASK_APP=hello where hello is the name of our python file hello.py
    # export FLASK_ENV=development
    # flask run

# If the program is named app.py
     # app.py is the defalut application  So you don't have toe do the export flask_app=filename
     # export FLASK_ENV=development
     # flask run

import numpy as np
import pandas as pd
import datetime as dt
from datetime import date
import os.path

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
connection = engine.connect()

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Stat_Location = Base.classes.station
Stat_measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
# the functionality of templates comes from Jinja (https://jinja.palletsprojects.com/en)
# the "request" was added becuase this there is a request on the page."

app = Flask(__name__)
app.secret_key = 'asdf8979a8sdfaehrrwasdfasdfa'

#################################################
# Flask Routes
#################################################
###############  Code for the home page #################################################################################
@app.route('/')
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"        
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f'/api/v1.0/<start>/<end><br>'
    )


###############  Code for the percipitation page #################################################################################
@app.route('/api/v1.0/precipitation')

def percipitation():
    session = Session(engine)
    results = session.query(Stat_measurement.date, Stat_measurement.prcp).all()
    session.close()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    df = pd.DataFrame(results, columns =['Date', 'Prcp'])
    dfi = df.set_index('Date')
    dfi = dfi.dropna(how='any')
    dfi.sort_index(inplace = True, ascending=True)
    prcp_dic = dfi.to_dict()
    prcp_dic
    return jsonify(prcp_dic)



###############  Code for the stations page #################################################################################
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results = session.query(Stat_measurement.station).distinct().all()
    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)



###############  Code for the temperature page #################################################################################
@app.route('/api/v1.0/tobs')
def temperature():
    """Return a list tobs for the last year from the most active station"""
    # Query the dates and temperature observations of the most active station for the previous year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.

    # query to select data from the most active station
    session = Session(engine)
    results = session.query(Stat_measurement.station, Stat_measurement.date, Stat_measurement.tobs).all()
    session.close()

    df = pd.DataFrame(results, columns =['Station', 'Date', 'tobs'])
    a = df.groupby(['Station']).size().sort_values(ascending=False)
    most_active = a.index[0]

    # The most resent date as string
    most_recent_record = session.query(Stat_measurement.date).order_by(Stat_measurement.date.desc()).first()  # add the desc() method to sort descending.
    most_recent_date_str = most_recent_record.date

    # convert that string to datatime
    most_recent_date = date.fromisoformat(most_recent_date_str)

    # Calculate the date one year from the last date in data set.
    one_year_ago = date((most_recent_date.year - 1), most_recent_date.month, most_recent_date.day).isoformat()

    # good to here

    # Perform a query to retrieve the data and precipitation scores
    # Query the last 12 months of temperature observation data for most active station
    session = Session(engine)
    results_temp = session.query(Stat_measurement.date,  Stat_measurement.tobs).\
        filter (Stat_measurement.date > one_year_ago).\
        filter (Stat_measurement.station == most_active).all()
    session.close()

    df_temp = pd.DataFrame(results_temp, columns =['Date', 'Temperature'])
    dfi_temp = df_temp.set_index('Date')
    dfi_temp = dfi_temp.dropna(how='any')
    dfi_temp.sort_index(inplace = True, ascending=True)
    temp_dic = dfi_temp.to_dict()
    #temp_dic
    return jsonify(temp_dic)


###############  Code for the start page #################################################################################
@app.route('/api/v1.0/<start>')
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for all dates greater than or equal to the start date.
def start(start):
    # save the start date
    #start_date = date.fromisoformat(start)

    while True:
        try:
            start_date = date.fromisoformat(start)
            break
        except ValueError:
            return (f'The correct date format is yyyy-mm-dd')
            break

    # query to date and temperatue for dates greater than or equal to the start date
    session = Session(engine)
    results = session.query(Stat_measurement.date, Stat_measurement.tobs). \
        filter (Stat_measurement.date >= start).all()
    session.close()

    df_temp = pd.DataFrame(results, columns =['Date', 'Temperature'])   #convert query to data frame
    dfi_temp = df_temp.set_index('Date')                                # set index to the date
    dfi_temp = dfi_temp.dropna(how='any')                               # drop the NaN
    dfi_temp.sort_index(inplace = True, ascending=True)                 # sort by date


    TMAX = round(dfi_temp.max()[0],2)                                   # find max and round to 2 digits
    TMIN = round(dfi_temp.min()[0],2)                                   # find min and round to 2 digits
    TAVG = round(dfi_temp.mean()[0],2)                                  # find average and round to 2 digits

    results = {'Start date':start , 'TMIN':TMIN , 'TAVG':TAVG, 'TMAX':TMAX}   # put results in a dictionary
    return  jsonify(results)                                            # return results

  

###############  Code for when a start and end page #################################################################################
@app.route('/api/v1.0/<start>/<end>')
def end(start, end):

    #save start and end dates
    #start_date = date.fromisoformat(start)
    #end_date = date.fromisoformat(end)

    while True:
        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
            break
        except ValueError:
            return (f'The correct date format is yyyy-mm-dd')
            break

    # return an error message if the end date is befor the start date
    if end_date < start_date:
        return (f'Error:  End date is before start date')

    # query to date and temperatue for dates greater than or equal to the start date and less than or equal to end
    session = Session(engine)
    results = session.query(Stat_measurement.date, Stat_measurement.tobs). \
        filter (Stat_measurement.date >= start_date). \
        filter (Stat_measurement.date <= end_date).all()
    session.close()

    df_temp = pd.DataFrame(results, columns =['Date', 'Temperature'])   #convert query to data frame
    dfi_temp = df_temp.set_index('Date')                                # set index to the date
    dfi_temp = dfi_temp.dropna(how='any')                               # drop the NaN
    dfi_temp.sort_index(inplace = True, ascending=True)                 # sort by date


    date_range = f'{start_date} to {end_date}'                          # set string for date rang                          
    TMAX = round(dfi_temp.max()[0],2)                                   # find max and round to 2 digits
    TMIN = round(dfi_temp.min()[0],2)                                   # find min and round to 2 digits
    TAVG = round(dfi_temp.mean()[0],2)                                  # find average and round to 2 digits

    results = {'Dates':date_range , 'TMIN':TMIN , 'TAVG':TAVG, 'TMAX':TMAX}  # put results in a dictionary
    return  jsonify(results)                                                 # return results



############################


if __name__ == '__main__':
    app.run(debug=True)


