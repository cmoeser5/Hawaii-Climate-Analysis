# set up and dependencies
from sqlalchemy import create_engine
from sqlalchemy import inspect
from pprint import pprint

# create engine from sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# create inspector
inspector = inspect(engine)

# create variable to inspect table names
table_names = inspector.get_table_names()
# print(table_names)
# table names are: 'measurement', 'station'

# create variables to inspect inspect column names in each table
measurement_column_names = inspector.get_columns("measurement")
station_column_names = inspector.get_columns("station")

#print out column names for each table to create classes
print("Measurement Column Names:")
pprint(measurement_column_names)
print("---------------------------")
print("Station Column Names:")
pprint(station_column_names)