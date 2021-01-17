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