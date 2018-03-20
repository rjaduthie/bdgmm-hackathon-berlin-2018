import os, requests

# create endpoint (although will probably not change)
fiesta_base_url = 'https://playground.fiesta-iot.eu/'
sparql_endpoint = 'iot-registry/api/queries/execute/global'
sparql_url = fiesta_base_url + sparql_endpoint

# add all the prefixes to all queries
prefixes = '''
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

def Select(*variables, distinct=False):
    select = "SELECT"
    if distinct:
        select += " DISTINCT"
    
    for variable in variables:
        select += " ?%s" % variable
    
    select += "\n"
    
    return select


def Where(*conditions,filters=None):
    where = "WHERE {"+"\n"
    for cond in conditions:
      where += cond+" .\n"
    
    if filters:
      where += filters
    
    where += "}"+"\n"
    return where


def FilterByTime(time_variable_str, datetime_from, datetime_to):
  filter = "FILTER ("+"\n"
  filter += '  ( xsd:dateTime(?%s) > xsd:dateTime("%s")) \n' % (time_variable_str, datetime_from.strftime("%Y-%m-%dT%H:%M:%SZ"))
  filter += '  &&  ( xsd:dateTime(?%s) < xsd:dateTime("%s")) \n' % (time_variable_str, datetime_to.strftime("%Y-%m-%dT%H:%M:%SZ"))
  filter += ") ."+"\n" 
  
  return filter

def OrderByAsc(variable=None):
    if variable is not None:
        return "ORDER BY ASC(?%s)" % variable
    else:
        return ""


def Limit(Limit=1000000):
    if type(Limit) is int:
        return "LIMIT %i" % Limit
    else:
        return ""

def SubmitQuery(sparql_query, time_range):
  
  
  # create headers for authorization
  # request token
  auth_headers = {'Content-Type':'application/json','X-OpenAM-Username':os.getenv('FIESTA_USERNAME'),'X-OpenAM-Password':os.getenv('FIESTA_PASSWORD')}
  auth_url = 'https://platform.fiesta-iot.eu/openam/json/authenticate'
  auth_response = requests.post(auth_url, headers=auth_headers)
  token_dict = auth_response.json()
  if 'tokenId' not in token_dict:
      sys.exit(1)
  token = token_dict['tokenId']
 
  query_headers = {'iPlanetDirectoryPro':token, 'Content-Type':'text/plain', 'Accept':'application/json'}
  
  if len(time_range) == 2:
    date_params = {'from':time_range[0].strftime('%Y%m%d%H%M%S'),'to':time_range[1].strftime('%Y%m%d%H%M%S')}
  
  query_response = requests.post(sparql_url, params = date_params, data=sparql_query, headers=query_headers)
  query_results = query_response.json()

  return query_results