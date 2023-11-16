# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# open connection
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Start at the homepage
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date<br/>"
        f"/api/v1.0/<start>/end<br/>"
    )

# precipitation analysis
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all precipitation
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).\
                filter(Measurement.date >= dt.date(2016,8,23)).all()

    # We have the data; now close the session
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation_list
    precipitation_list = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)
    print(precipitation_list)
    
    # Return the JSON representation of your dictionary
    return jsonify(precipitation_list)

#stations list
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations    
    results = session.query(Station.station).all()

    # We have the data; now close the session    
    session.close()

    # Reformat results so we can JSONify them
    all_stations = list(np.ravel(results))

    # Return a JSON list of stations
    return jsonify(all_stations)

# dates & temps from the most-active station (USC00519281)
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most-active station for the previous year of data
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station=='USC00519281').\
        order_by(Measurement.date).\
        filter(Measurement.date >= dt.date(2016,8,23)).all()               

    # We have the data; now close the session
    session.close()
    
    # Reformat results so we can JSONify them
    tobs = list(np.ravel(results))
    
    # Return a JSON list of temperature observations for the previous year
    return jsonify(tobs)

# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start

@app.route("/api/v1.0/<start>")

def start(start):

    # For a specified start, calculate TMIN, TAVG, and TMAX 
    # for all the dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
                            func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    # We have the data; now close the session
    session.close()

    # Return a JSON list of results
    return jsonify(results)

# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start-end range

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX 
    # for the dates from the start date to the end date, inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
                            func.max(Measurement.tobs)).filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()

    # We have the data; now close the session
    session.close()
    
    # Return a JSON list of results
    return jsonify(results)

if __name__ == '__main__':
    app.run()
    
session.close()