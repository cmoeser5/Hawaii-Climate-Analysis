# Hawaii Climate Analysis

### Background
Used Python and SQLAlchemy to do basic climate analysis and data exploration of a Hawaii climate database that contains precipitation and temperature observations across 9 stations. Created a Flask API based on the analysis and SQLAlchemy ORM queries.

### Technologies Used
* Python
* SQLAlchemy
* Panadas
* Matplotlib

### Data Analysis and Exploration
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

Climate Anaylsis: Obtained the last 12 months of precipiation data, converted into a dataframe, and plotted a bar chart.

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

Station Analysis: Calculated total number of stations, found the most active stations by highest number of observations, obtained the last 12 months of temperature data for the most active station, and converted to a dataframe to plot a histogram

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