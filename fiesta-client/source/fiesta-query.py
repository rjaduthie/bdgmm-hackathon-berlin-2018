# the interface to the SPARQL endpoint can be done with: 
# - sparql-client package...but the documentation is missing
# - sparqlwrapper

from SPARQLWrapper import SPARQLWrapper, JSON

sparql_query_prefixes = '''

PREFIX iot-lite: <http://purl.oclc.org/NET/UNIS/fiware/iot-lite#>
PREFIX m3-lite: <http://purl.oclc.org/iot/vocab/m3-lite#>
PREFIX ssn: <http://purl.oclc.org/NET/ssnx/ssn#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dul:  <http://www.loa.istc.cnr.it/ontologies/DUL.owl#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX sics: <http://smart-ics.ee.surrey.ac.uk/fiesta-iot#>

'''

sparql_query_select = '''

SELECT ?sensingDevice ?dataValue ?dateTime

'''

sparql_query_where = '''
WHERE {
	?sensingDevice a m3-lite:EnergyMeter .
	?sensingDevice iot-lite:hasQuantityKind ?qk .
	?qk a m3-lite:Power .
	?sensingDevice iot-lite:hasUnit ?unit .
	?device a ssn:Device .
	?device ssn:onPlatform ?platform .
	?platform geo:location ?point .
	?point geo:lat ?lat .
	?point geo:long ?long .
	?observation ssn:observedBy ?sensingDevice .
	?observation ssn:observationalResult ?sensorOutput .
	?sensorOutput ssn:hasValue ?obsValue .
	?obsValue dul:hasDataValue ?dataValue .
	?observation ssn:observationSamplingTime ?instant .
	?instant time:inXSDDateTime ?dateTime
	.
	#set interval
	FILTER (
			( xsd:dateTime(?dateTime) > xsd:dateTime("2018-02-15T00:00:00Z"))
		&& 	( xsd:dateTime(?dateTime) < xsd:dateTime("2018-02-16T00:00:00Z"))
	) 
	#set location
	.
	FILTER (
	       ( xsd:double(?lat) >= "0"^^xsd:double)
	 &&    ( xsd:double(?lat) <= "60"^^xsd:double)
	 &&    ( xsd:double(?long) >= "0"^^xsd:double)
   &&    ( xsd:double(?long) >= "-6"^^xsd:double)
	) .
}
'''
sparql_query_order = '''
ORDER BY ?sensingDevice ASC(?dateTime)
'''

sparl_query_limit = '''
LIMIT 100000
'''

sparql_query =  sparql_query_prefixes + sparql_query_select + sparql_query_where + sparql_query_order + sparl_query_limit

fiesta_base_url = 'https://playground.fiesta-iot.eu/'
sparql_endpoint = 'iot-registry/api/queries/execute/global'

sparql = SPARQLWrapper(fiesta_base_url + sparql_endpoint)

sparql.setQuery(sparql_query)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
  print(result["label"]["value"])