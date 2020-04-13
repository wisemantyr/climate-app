import numpy as np
import pandas as pd
from scipy import stats 

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine,reflect=True)


Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

app = Flask(__name__)

DateFormat = "%Y-%m-%d"

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>" 
        f"/api/v1.0/<start>/<end><br>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    LastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    YearBeforeLastDate = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    YearBeforeLastDateString = YearBeforeLastDate.strftime(DateFormat)
    PrcpData = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= YearBeforeLastDateString).all()
    PrcpDict = dict(PrcpData)
    return jsonify (PrcpDict)
    
#Convert the query results to a dictionary using date as the key 
#and prcp as the value.
#Return the JSON representation of your dictionary.


@app.route("/api/v1.0/stations")
def station():
    StationList = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    return jsonify (StationList)

#Return a JSON list of stations from the dataset.


@app.route("/api/v1.0/tobs")
def tobs():
    StationFrequency = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    MostActiveStation = StationFrequency[0][0]
    TempMostActive = session.query(Measurement.tobs).filter(Measurement.station == MostActiveStation).all()
    LowTemp = min(TempMostActive)
    HighTemp = max(TempMostActive)
    AvgTemp = round(np.average(TempMostActive),2)
    LastDateMostActive = session.query(Measurement.date).filter(Measurement.station == MostActiveStation).order_by(Measurement.date.desc()).first()
    YearBefore = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    YearBeforeString = YearBefore.strftime(DateFormat)
    TempData = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= YearBeforeString, Measurement.station == MostActiveStation).all()
    summary = {"most-active-station": MostActiveStation,
    "lowest-temp": LowTemp,
    "highest-temp": HighTemp,
    "average-temp": AvgTemp}
    return jsonify(summary, TempData)

#Query the dates and temperature observations of the most active 
#station for the last year of data.
#Return a JSON list of temperature observations (TOBS) 
#for the previous year.

@app.route("/api/v1.0/<start>")
def startonly(start):
    TempDataStart = session.query(Measurement.tobs).filter(Measurement.date >= start).all()
    LowTempStart = min(TempDataStart)
    HighTempStart = max(TempDataStart)
    ConvertedDataStart = [x[0] for x in TempDataStart]
    AvgTempStart = round(np.average(ConvertedDataStart),2)
    summary = {"lowest-temp": LowTempStart,
    "highest-temp": HighTempStart,
    "average-temp": AvgTempStart}
    return jsonify(summary)

#TMINStart = stats.tmin(TempDataStart)
#TMAXStart = stats.tmax(TempDataStart)

#Return a JSON list of the minimum temperature, 
#the average temperature, and the max temperature 
#for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX 
#for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    TempDataEnd = session.query(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    LowTempEnd = min(TempDataEnd)
    HighTempEnd = max(TempDataEnd)
    ConvertedDataEnd = [y[0] for y in TempDataEnd]
    AvgTempEnd = round(np.average(ConvertedDataEnd),2)
    summary = {"lowest-temp": LowTempEnd,
    "highest-temp": HighTempEnd,
    "average-temp": AvgTempEnd}
    return jsonify(summary)

 #When given the start and the end date, 
 #calculate the TMIN, TAVG, and TMAX for dates 
#between the start and end date inclusive.

if __name__ == '__main__':
    app.run(debug=True)