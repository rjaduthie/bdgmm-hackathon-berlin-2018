# this file will obtain the timeseries data for all temp sensors in a time window
# the time window can only be 6 hours and is set by query parameters:
# from=yyyymmddhhMM&to=...etc...

import requests, os, json, sys, datetime
import fiesta_sparql as fsparql


start_datetime = datetime.datetime(year=2018,month=2,day=1,hour=0,minute=0,second=0)
stop_datetime = datetime.datetime(year=2018,month=3,day=1,hour=0,minute=0,second=0)

def datetime_generator(start, stop):
  for n in range(int((stop-start).days*4)+1):
    yield start+datetime.timedelta(hours=n*6)
  
for from_datetime in datetime_generator(start_datetime, stop_datetime):
  
  to_datetime = from_datetime + datetime.timedelta(hours=5,minutes=59)
  
  # build SPARQL query
  
  sparql_query = fsparql.prefixes
  sparql_query += fsparql.Select('sensingDevice','dateTime','dataValue')
  where_conditions = ['?sensingDevice iot-lite:hasQuantityKind/rdf:type ?qk',
                      'values ?qk {m3-lite:Temperature m3-lite:AirTemperature m3-lite:RoomTemperature}',                    
                      '?sensingDevice ssn:madeObservation ?obs',
                      '?obs ssn:observationSamplingTime ?instant',
                      '?instant time:inXSDDateTime ?dateTime',
                      '?obs ssn:observationResult ?sensorResult',
                      '?sensorResult ssn:hasValue ?obsVal',
                      '?obsVal dul:hasDataValue ?dataValue']
  
  sparql_query += fsparql.Where(*where_conditions,filters=fsparql.FilterByTime('dateTime',from_datetime,to_datetime))
  
  sparql_query += fsparql.OrderByAsc('dateTime') #order by device URL
  
  query_results = fsparql.SubmitQuery(sparql_query, time_range=[from_datetime, to_datetime])
  
  if 'items' not in query_results:
      sys.exit(1)
      
  sensor_url = []
  date_time = []
  temperature = []
  
  for result in query_results['items']:
    sensor_url_str = result['sensingDevice']
    sensor_url.append(sensor_url_str)
  
    date_time_str = result['dateTime'].split('^')[0]
  #   date_time_val = datetime.strptime(date_time_str)
  #   date_time.append(datetime.strftime(date_time_val,'%Y%m%d %H:%m:%s.%ms')
    date_time.append(date_time_str)
    
    temperature_str = result['dataValue'].split('^')[0]
    temperature_val = float(temperature_str)
    temperature.append(temperature_val)
  
  # now output these data to a CSV
  import itertools
  sensor_data = itertools.zip_longest(date_time,temperature,sensor_url,fillvalue='NaN') # fillvalue compatible with javascript isNaN()
    
  import csv
  with open('data/sensors_data_%s.csv' % from_datetime.strftime("%Y%m%d-%H%M"), 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(('date_time','temperature','sensor_url'))
      writer.writerows(sensor_data)


  
