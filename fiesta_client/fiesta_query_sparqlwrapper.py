# the interface to the SPARQL endpoint can be done with: 
# - sparql-client package...but the documentation is missing
# - sparqlwrapper

from SPARQLWrapper import SPARQLWrapper, JSON, CSV

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
sparql_query_order = '''
ORDER BY ?sensingDevice ASC(?platform)
'''

sparl_query_limit = '''
LIMIT 100000
'''

sparql_query =  sparql_query_prefixes + sparql_query_select + sparql_query_where + sparql_query_order + sparl_query_limit

fiesta_base_url = 'https://playground.fiesta-iot.eu/'
sparql_endpoint = 'iot-registry/api/queries/execute/global'
url = fiesta_base_url + sparql_endpoint

sparql = SPARQLWrapper(url)
# the reason this doesn't work is that there is no authorization information in the request

sparql.setQuery(sparql_query)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

print(len(results))

for result in results:
	print(result['qk'])
	print(result['lat'])
	print(result['long'])
	