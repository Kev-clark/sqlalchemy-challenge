from flask import Flask, jsonify
import pandas as pd
import numpy as np

from matplotlib import style
style.use('fivethirtyeight')

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from datetime import datetime as dt
from datetime import timedelta
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcom to the Weather App"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/tobs/startdate<br>"
        f"start date must be in '%Y-%m-%d' format Example: 2016-06-06<br>"
        f"/api/v1.0/temprange/startdate/enddate<br/>"
        f"start date and end date must be in '%Y-%m-%d' format Example: 2016-06-06"
    )

  # Home page.

  # List all routes that are available.

@app.route("/api/v1.0/precipitation")
def precipitation():
      session = Session(engine)
      Measurement = Base.classes.measurement
      Station = Base.classes.station
      #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
      df=pd.DataFrame(session.query(Measurement.date, Measurement.prcp).all(), columns=['Date', 'Precepitation'])
#Return the JSON representation of your dictionary.
      session.close()
      return jsonify(df.to_json())

  #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.



@app.route("/api/v1.0/stations")
def stations():
  # Return a JSON list of stations from the dataset.
      session=Session(engine)
      Measurement = Base.classes.measurement
      Station = Base.classes.station
      Station_List=pd.DataFrame(session.query(Measurement.station), columns=['Station count'])
      Station_List=pd.DataFrame(pd.value_counts(Station_List['Station count']), columns=['Station count'])
      session.close()
      Station_List["Station ID"]=Station_List.index
      return jsonify(pd.DataFrame(Station_List.index, columns=["Station ID"]).to_json())
      

  

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    Measurement = Base.classes.measurement
    Station = Base.classes.station
  #query for the dates and temperature observations from a year from the last data point.
    for x in session.query(Measurement.date).order_by(Measurement.date.desc()).first():
      last_date=x
    oneyearago= dt.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)
    oneyearago=dt.strftime(oneyearago, '%Y-%m-%d')
    datelist=[]
    tobslist=[]
    results=session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= oneyearago).group_by(Measurement.date).all()
    for x in results:
      datelist.append(x.date)
      tobslist.append(x.tobs)
    datalist={'Date':datelist, 
      'Tobs':tobslist

    }
    df=pd.DataFrame(datalist)
  
    
    
    
    session.close()
    
    return jsonify(df.to_json())
  
   

@app.route("/api/v1.0/tobs/<start>")
def startdate(start):
  startdate=dt.strptime(start,'%Y-%m-%d' )
  startdate=dt.strftime(startdate, '%Y-%m-%d' )
#Return a JSON list of Temperature Observations (tobs) for the previous year.
  session=Session(engine)
  Measurement = Base.classes.measurement
  Station = Base.classes.station
 

  oneyearago= dt.strptime(startdate, '%Y-%m-%d') - timedelta(days=365)
  oneyearago=dt.strftime(oneyearago, '%Y-%m-%d')
  datelist=[]
  tobslist=[]
  results=session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= oneyearago).all()
  
  df=pd.DataFrame(results, columns=["Date", "Tempurature"])
  df.set_index("Date", inplace=True)
  
    
    
    
  session.close()
    
  return jsonify(df.to_json())
@app.route("/api/v1.0/temprange/<start>/<end>")
def temprange(start=None, end=None):
  session=Session(engine)
  startdate=dt.strptime(start,'%Y-%m-%d' )
  startdate=dt.strftime(startdate, '%Y-%m-%d' )
  
  if end == None:
      end="2016-08-23"   
  
  enddate=dt.strptime(end,'%Y-%m-%d' )
  enddate=dt.strftime(enddate, '%Y-%m-%d' )
  if dt.strptime(start,'%Y-%m-%d' ) > dt.strptime(end,'%Y-%m-%d' ):
    return jsonify("Not a valid search")
  
  # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

  # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
  def calc_temps(start_date, end_date):
  #  """TMIN, TAVG, and TMAX for a list of dates.
  # Args:
  #    start_date (string): A date string in the format %Y-%m-%d
  #    end_date (string): A date string in the format %Y-%m-%d 
  #Returns:
   #     TMIN, TAVE, and TMAX
            return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
  return jsonify(calc_temps(startdate, enddate))
  # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
if __name__ == '__main__':
    app.run(debug=True)
