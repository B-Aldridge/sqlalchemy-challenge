# -*- coding: utf-8 -*-
"""
Created on Sat May  6 18:10:50 2023

@author: joshu
"""
#Import Dependencies
from flask import Flask, jsonify
import datetime as dt
import numpy as np
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################

# Create an engine to connect to the SQLite database file
engine = create_engine("sqlite:///sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the Measurement and Station tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session to interact with the database
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Create an instance of Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    # Provide information about the available routes
    return (
        f"Welcome to the Hawaii Climate API!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Retrieve the last 12 months of precipitation data<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"- Retrieve a list of stations<br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Retrieve the last 12 months of temperature observations for the most active station<br/><br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"- Retrieve the minimum, average, and maximum temperatures from a specified start date (format: YYYY-MM-DD)<br/><br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
        f"- Retrieve the minimum, average, and maximum temperatures within a specified date range (format: YYYY-MM-DD/YYYY-MM-DD)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    # Calculate the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    
    # Calculate the date one year ago from the last date
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query the date and precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in results}
    
    # Close the session
    session.close()
    
    # Return the JSON representation of the precipitation data
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query the list of stations
    results = session.query(Station.station).all()
    
    # Flatten the query results and convert them to a list
    station_list = list(np.ravel(results))
    
    # Return the JSON representation of the station list
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the last 12 months of temperature observations for the most active station."""
    # Calculate the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    # Calculate the date one year ago from the last date
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first().station

    # Query the date and temperature observations for the last 12 months for the most active station
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).filter(Measurement.station == most_active_station).all()

    # Create a list of dictionaries containing date and temperature observations
    temperature_data = [{"date": date, "tobs": tobs} for date, tobs in results]

    # Return the JSON representation of the temperature data
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    """Return the minimum, average, and maximum temperatures from a specified start date."""
    # Convert the start date string to a datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # Query the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    # Create a dictionary with the start date and temperature statistics
    temperature_stats = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    # Return the JSON representation of the temperature statistics
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    """Return the minimum, average, and maximum temperatures within a specified date range."""
    # Convert the start and end date strings to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    # Query the minimum, average, and maximum temperatures for dates within the specified range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Create a dictionary with the start date, end date, and temperature statistics
    temperature_stats = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    # Return the JSON representation of the temperature statistics
    return jsonify(temperature_stats)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
    



