import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

Base=automap_base()
Base.prepare(engine, reflect=True)

Measurements=Base.classes.measurement
Station=Base.classes.station

app=Flask(__name__)

@app.route("/")
def welcome():
    
    return(
        f"List all available API routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def Precipitation():
    session=Session(engine)
    results=session.query(Measurements.date, Measurements.prcp).\
                order_by(Measurements.date).all()
    prcp_list=[]
    for date, prcp in results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_list.append(new_dict)    
    
    session.close()

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def Stations():
    session=Session(engine)
    stations={}
    results=session.query(Station.station, Station.name).all()
    for s,name in results:
        stations[s]=name
    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    
    last_date=session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    
    last_year_date=(dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    results =   session.query(Measurements.date, Measurements.tobs).\
                filter(and_(Measurements.date >=last_year_date, Measurements.station== "USC00519281")).\
                order_by(Measurements.date).all()

    tobs_date_list = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_list.append(new_dict)

    session.close()

    return jsonify(tobs_date_list)

@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    session=Session(engine)
    return_list=[]
    results=session.query(Measurements.date, func.min(Measurements.tobs),\
                          func.avg(Measurements.tobs),\
                          func.max(Measurements.tobs)).\
                    filter(Measurements.date >=start).\
                    group_by(Measurements.date).all()
    for date, min,avg,max in results:
        new_dict={}
        new_dict["Date"]=date
        new_dict["TMIN"]=min
        new_dict["TAVG"]=avg
        new_dict["TMAX"]=max
        return_list.append(new_dict)
    
    session.close()

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    session=Session(engine)

    return_list=[]

    results=session.query(Measurements.date, func.min(Measurements.tobs),\
                          func.avg(Measurements.tobs),\
                          func.max(Measurements.tobs)).\
                    filter(and_(Measurements.date >=start, Measurements.date<= end)).\
                    group_by(Measurements.date).all()
    for date, min,avg,max in results:
        new_dict={}
        new_dict["Date"]=date
        new_dict["TMIN"]=min
        new_dict["TAVG"]=avg
        new_dict["TMAX"]=max
        return_list.append(new_dict)
    
    session.close()

    return jsonify(return_list)

if __name__ == "__main__":
    app.run(debug=True)