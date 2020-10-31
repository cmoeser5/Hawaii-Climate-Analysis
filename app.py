import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite",
                       connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Hawaii Climate Analysis<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query Measurement
    results = (session.query(Measurement.date, Measurement.tobs)
                      .order_by(Measurement.date))
    
    # Create a dictionary
    precipitation_date_tobs = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["tobs"] = each_row.tobs
        precipitation_date_tobs.append(dt_dict)

    return jsonify(precipitation_date_tobs)


@app.route("/api/v1.0/stations")
def stations():

    # Query Measurement
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))
    return jsonify(station_details)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Convert list of tuples into normal list
    temps_detail = list(np.ravel(results))

    return jsonify(temps_detail)


@app.route("/api/v1.0/<start>")
def start_only(start):
    
    # Query the max date
    date_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_max_str = str(date_max)
    date_max_str = re.sub("'|,", "",date_max_str)
    print (date_max_str)
    
    # Query the min date
    date_min = session.query(Measurement.date).first()
    date_min_str = str(date_min)
    date_min_str = re.sub("'|,", "",date_min_str)
    print (date_min_str)
    
    # Check for valid start date
    start_entry = session.query(exists().where(Measurement.date == start)).scalar()
 
    if start_entry:

        results = (session.query(func.min(Measurement.tobs)
                    ,func.avg(Measurement.tobs)
                    ,func.max(Measurement.tobs))
                   .filter(Measurement.date >= start).all())

        tmin =results[0][0]
        tavg ='{0:.2}'.format(results[0][1])
        tmax =results[0][2]
    
        result_temps =( ['Entered Start Date: ' + start,
                            'Lowest Temperature: '  + str(tmin),
                            'Average Temperature: ' + str(tavg),
                            'Highest Temperature: ' + str(tmax)])
        return jsonify(result_temps)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end():
    
    # Query the max date
    date_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_max_str = str(date_max)
    date_max_str = re.sub("'|,", "",date_max_str)
    print (date_max_str)
    
    # Query the min date
    date_min = session.query(Measurement.date).first()
    date_min_str = str(date_min)
    date_min_str = re.sub("'|,", "",date_min_str)
    print (date_min_str)
    
     # Check for valid start date
    start_entry = session.query(exists().where(Measurement.date == start)).scalar()
    
     # Check for valid end date
    end_entry = session.query(exists().where(Measurement.date == end)).scalar()
    
    if start_entry and end_entry:

        results = (session.query(func.min(Measurement.tobs)
                    ,func.avg(Measurement.tobs)
                    ,func.max(Measurement.tobs))
                        .filter(Measurement.date >= start)
                        .filter(Measurement.date <= end).all())

        tmin =results[0][0]
        tavg ='{0:.2}'.format(results[0][1])
        tmax =results[0][2]
    
        result_temps=( ['Entered Start Date: ' + start,
                            'Entered End Date: ' + end,
                            'Lowest Temperature: '  + str(tmin),
                            'Average Temperature: ' + str(tavg),
                            'Highest Temperature: ' + str(tmax)])
        return jsonify(result_temps)



if __name__ == '__main__':
    app.run(debug=True)