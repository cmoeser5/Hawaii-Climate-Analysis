# Hawaii Climate Analysis

## Background
Used Python and SQLAlchemy to do basic climate analysis and data exploration of a Hawaii climate database that contains precipitation and temperature observations across 9 stations. Created a Flask API based on the analysis and SQLAlchemy ORM queries.

## Technologies Used
* Python
* SQLAlchemy
* Panadas
* Matplotlib

## Data Analysis and Exploration
Set up base, created classes for each table and connected to the sqlite database.

```python
# connect to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()
session = Session(bind=engine)
inspector = inspect(engine)

# set up Base
Base = declarative_base()

# create classes for measurement and station table
class Measurement(Base):
    __tablename__ = "measurement"
    id = Column(Integer, primary_key=True)
    station = Column(String(30))
    date = Column(Date)
    prcp = Column(Float)
    tobs = Column(Float)


class Station(Base):
    __tablename__ = "station"
    id = Column(Integer, primary_key=True)
    station = Column(String(30))
    name = Column(String(120))
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
```

### Climate Anaylsis: 
Obtained the last 12 months of precipiation data, converted into a dataframe, and plotted a bar chart.

```python
# design a query to retrieve the last 12 months of precipitation data and plot the results
query = (
    session.query(Measurement.date, func.avg(Measurement.prcp))
    .filter(Measurement.date >= start_date)
    .filter(Measurement.date <= end_date)
    .group_by(Measurement.date)
)

# save the query results as a Pandas DataFrame and set the index to the date column
prcp_df = (
    pd.read_sql(query.statement, query.session.bind, index_col="date")
    .rename(columns={"avg_1": "precipitation"})
    .sort_index()
)

# using Pandas plotting with Matplotlib to plot the data
prcp_df.plot(
    kind="bar",
    title="Average Daily Precipitation at Hawaii Weather Stations",
    figsize=(10, 10),
    width=3,
    legend=False,
)
plt.locator_params(axis="x", nbins=9.5)
plt.xlabel("Date")
plt.ylabel("Inches")
plt.savefig("Images/precipitation_bar.png")
plt.show()
```

![bar](Images/precipitation_bar.png)

### Station Analysis: 
Calculated total number of stations, found the most active stations by highest number of observations, obtained the last 12 months of temperature data for the most active station, and converted to a dataframe to plot a histogram

```python
# query to show how many stations are available in this dataset
num_station_measurement = len(session.query(Measurement.station).distinct().all())

num_station = len(session.query(Station.station).distinct().all())

# find the most active station

active_station = (
    session.query(Measurement.station, func.count(Measurement.station))
    .group_by(Measurement.station)
    .order_by(func.count(Measurement.station).desc())
)

# get the last 12 months of temperature observation data for station USC00519281
min_date, max_date = (
    session.query(func.min(Measurement.date), func.max(Measurement.date))
    .filter(Measurement.station == "USC00519281")
    .first()
)

start_date = max_date - relativedelta(years=1)
end_date = max_date

query = (
    session.query(Measurement.date, Measurement.tobs)
    .filter(Measurement.station == "USC00519281")
    .filter(Measurement.date >= start_date)
    .filter(Measurement.date <= end_date)
)

# convert to a dataframe
temp_df = (
    pd.read_sql(query.statement, query.session.bind, index_col="date")
    .rename(columns={"tobs": "temperature"})
    .sort_index()
)

# plot a histogram of the results
temp_df.plot(
    kind="hist", title="Temperature Reportings", bins=12, legend=False, figsize=(8, 8)
)
plt.xlabel("Temp(F)")
plt.ylabel("Frequency")
plt.savefig("Images/histogram.png")
plt.show()
```
![histogram](Images/histogram.png)

### Temperature Analysis:
Analyzed min, max and avg temperatures for a specific date range using previous years data. Plotted the min, max and avg temperatures from the query on a bar chart.

```python
# create a function that will accept start date and end date, returning the min, avg and max temps for a date range
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    return (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start_date)
        .filter(Measurement.date <= end_date)
        .all()
    )

# using function `calc_temps` to calculate the tmin, tavg, and tmax for date range using the previous year's data for those same dates.
prev_year_start = dt.date(2018, 5, 1) - dt.timedelta(days=365)
prev_year_end = dt.date(2018, 5, 7) - dt.timedelta(days=365)

tmin, tavg, tmax = calc_temps(
    prev_year_start.strftime("%Y-%m-%d"), prev_year_end.strftime("%Y-%m-%d")
)[0]

# plot the results in a bar chart and use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)
tmin = t[0][0]
tavg = t[0][1]
tmax = t[0][2]
yerr = tmax - tmin

plt.figure(figsize=(2, 10))
plt.bar(0, tavg, yerr=yerr, align="center", width=1, color="blue", alpha=0.5)
plt.ylim = (0, 100)
plt.ylabel("average temperature(F)")
plt.title("Trip Avg Temp")
plt.savefig("Images/avg_temp.png")
plt.show()
```

![avg_temp](Images/avg_temp.png)

### Daily Rainfall Average:
Calculated the rainfall per weather station using the years previous matching for the date range.

```python
# calculate the rainfall per weather station using previous year's matching dates
start_date = "2017-05-01"
end_date = "2017-05-07"

sel = [
    Station.station,
    Station.name,
    Station.latitude,
    Station.longitude,
    Station.elevation,
    func.sum(Measurement.prcp),
]

results = (
    session.query(*sel)
    .filter(Measurement.station == Station.station)
    .filter(Measurement.date >= start_date)
    .filter(Measurement.date <= end_date)
    .group_by(Station.name)
    .order_by(func.sum(Measurement.prcp).desc())
    .all()
)
```
### Daily Temperature Normals:
Calculated the daily minimum, maximum, and average temperatures for the tip date range and the plotted the results on an area plot.

```python
# define daily normals function
def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """

    sel = [
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]
    return (
        session.query(*sel)
        .filter(func.strftime("%m-%d", Measurement.date) == date)
        .all()
    )

# calculate the daily normals for trip range

trip_start = "2018-05-01"
trip_end = "2018-05-07"

# use the start and end date to create a range of dates
trip_dates = pd.date_range(trip_start, trip_end, freq="D")

trip_month_day = trip_dates.strftime("%m-%d")

# loop through the list of %m-%d strings and calculate the normals for each date
normals = []
for date in trip_month_day:
    normals.append(*daily_normals(date))
normals

# create a dataframe for date range and temp normals
df = pd.DataFrame(normals, columns=["tmin", "tavg", "tmax"])
df["date"] = trip_month_day
df.set_index(["date"], inplace=True)

# create an area plot
df.plot(kind="area", stacked=False, x_compat=True, alpha=0.2)
plt.tight_layout()
plt.xlabel("Date")
plt.savefig("Images/area_plot.png")
plt.ylabel("Temperature")
```

![area_plot](Images/area_plot.png)


## Flask API Design
Designed a Flask API based on the queries that were developed during the analysis above.

```python
# create session and engine to link to database
engine = create_engine("sqlite:///hawaii.sqlite",
                       connect_args={'check_same_thread': False})
session = Session(engine)

# establish app
app = Flask(__name__)
```

#### Homepage Route
Created this route to show all available routes for the API.

```python
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis App Homepage!<br/>"
        f"Available Routes Below:<br/>"
        f"Precipitation measurement over the last 12 months: /api/v1.0/precipitation<br/>"
        f"A list of stations and their respective station numbers: /api/v1.0/stations<br/>"
        f"Temperatures observations at the most active station over the previous 12 months: /api/v1.0/tobs<br/>"
        f"Enter a start date (yyyy-mm-dd) to retrieve the minimum, maximum, and average temperatures for all dates after the specified date: /api/v1.0/<start><br/>"
        f"Enter both a start and end dates (yyyy-mm-dd) to retrieve the minimum, maximum and average temperatures for that date range: /api/v1.0/<start>/<end>"
    )
```
#### Precipitation Route
This route will show the precipitation measurements over the last 12 months.

```python
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
```

#### Stations Route
This route will show a list of all the stations in Hawaii and their respective station numbers.

```python
@app.route("/api/v1.0/stations")
def stations():

    # Query Measurement
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))
    return jsonify(station_details)
```

#### Temperature Observation Route
This route will show the temperature observations at the most active station over the last 12 months.

```python
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
```

#### Start-End for Given Dates Route
These routes will show the minimum, maximum and average temperatures for either a specified start date or a range of dates.

```python
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
def start_end(start_entry, end_entry):
    
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
```