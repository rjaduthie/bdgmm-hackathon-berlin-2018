# the interface to the SPARQL endpoint can be done with: 
# - sparql-client package...but the documentation is missing
# - sparqlwrapper
# - requests

import requests, os, json, sys
import fiesta_sparql as fsparql  

# build SPARQL query

sparql_query = fsparql.prefixes
sparql_query += fsparql.Select('sensingDevice','lat','long','qk',distinct=True)
where_conditions = ['?sensingDevice iot-lite:hasQuantityKind/rdf:type ?qk',
                    'values ?qk {m3-lite:Temperature m3-lite:AirTemperature m3-lite:RoomTemperature}',
                    '?sensingDevice iot-lite:isSubSystemOf ?device',
                    '?device a ssn:Device',
                    '?device ssn:onPlatform ?platform',
                    '?platform geo:location ?point',
                    '?point geo:lat ?lat',
                    '?point geo:long ?long']

sparql_query += fsparql.Where(*where_conditions)
sparql_query += fsparql.OrderByAsc('long') #order east to west

query_results = fsparql.SubmitQuery(sparql_query)

if 'items' not in query_results:
    sys.exit(1)

n_sensors = len(query_results['items'])
sensor_url = []
sensor_type = []
sensor_lat = []
sensor_long = []

# the next part parses the data - this could be made more generalised, but it doesn't need to be currently
for result in query_results['items']:
	
    sensor_url_str = result['sensingDevice']
    sensor_url.append(sensor_url_str)
#     print('Attribute (url): %s' % result['sensingDevice'])
    
    type_str = result['qk'].split('#')[-1]
#     print('Attribute (qk): %s' % result['qk'])
#     print('Parsed: %s' % type_str)
    sensor_type.append(type_str)
    
    lat_str = result['lat'].split('^')[0]
    lat_val = float(lat_str)
#     print('Attribute (lat): %s' % result['lat'])
#     print('Parsed: %f' % lat_val)
    sensor_lat.append(lat_val)
    
    long_str = result['long'].split('^')[0]
    long_val = float(long_str)
#     print('Attribute (lat): %s' % result['long'])
#     print('Parsed: %f' % long_val)
    sensor_long.append(long_val)
    
# now output these data to a CSV
import itertools
sensor_info = itertools.zip_longest(sensor_type,sensor_lat,sensor_long,sensor_url,fillvalue='NaN') # fillvalue compatible with javascript isNaN()
	
import csv
with open('data/sensors_lat_long.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(('sensor_type','lat','long','sensor_url'))
    writer.writerows(sensor_info)
