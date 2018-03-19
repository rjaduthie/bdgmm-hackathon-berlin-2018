# the interface to the SPARQL endpoint can be done with: 
# - sparql-client package...but the documentation is missing
# - sparqlwrapper
# - requests

import requests, os, json, sys


# build SPARQL query

sparql_query_prefixes = '''
PREFIX iot-lite: <http://purl.oclc.org/NET/UNIS/fiware/iot-lite#>
PREFIX m3-lite: <http://purl.org/iot/vocab/m3-lite#>
PREFIX ssn: <http://purl.oclc.org/NET/ssnx/ssn#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dul:  <http://www.loa.istc.cnr.it/ontologies/DUL.owl#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX sics: <http://smart-ics.ee.surrey.ac.uk/fiesta-iot#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
'''

sparql_query_select = '''
SELECT DISTINCT ?sensingDevice ?qk ?lat ?long
'''

sparql_query_where = '''
WHERE {
  ?sensingDevice iot-lite:hasQuantityKind/rdf:type ?qk .
  values ?qk {m3-lite:Temperature m3-lite:AirTemperature m3-lite:RoomTemperature} .
  ?sensingDevice iot-lite:isSubSystemOf ?device .
  ?device a ssn:Device .
  ?device ssn:onPlatform ?platform .
  ?platform geo:location ?point .
  ?point geo:lat ?lat .
  ?point geo:long ?long
}
'''

# order west to east
sparql_query_order = ''' 
ORDER BY ASC(?long)
'''

sparl_query_limit = '''
LIMIT 100000
'''

sparql_query =  sparql_query_prefixes + sparql_query_select + sparql_query_where + sparql_query_order + sparl_query_limit


# create endpoint (although will probably not change)
fiesta_base_url = 'https://playground.fiesta-iot.eu/'
sparql_endpoint = 'iot-registry/api/queries/execute/global'
query_url = fiesta_base_url + sparql_endpoint

# create headers for authorization
# request token
# curl  --request POST --header "Content-Type: application/json"  --header "X-OpenAM-Username: $FIESTA_USERNAME"  --header "X-OpenAM-Password: $FIESTA_PASSWORD" --data "{}" https://platform.fiesta-iot.eu/openam/json/authenticate > fiesta-token.json
auth_headers = {'Content-Type':'application/json','X-OpenAM-Username':os.getenv('FIESTA_USERNAME'),'X-OpenAM-Password':os.getenv('FIESTA_PASSWORD')}
auth_url = 'https://platform.fiesta-iot.eu/openam/json/authenticate'
auth_response = requests.post(auth_url, headers=auth_headers)
token_dict = auth_response.json()
if 'tokenId' not in token_dict:
    sys.exit(1)

token = token_dict['tokenId']

query_headers = {'iPlanetDirectoryPro':token, 'Content-Type':'text/plain', 'Accept':'application/json'}

query_response = requests.post(query_url, data=sparql_query, headers=query_headers)

query_results = query_response.json()

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
