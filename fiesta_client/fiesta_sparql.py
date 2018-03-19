
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

def select(*variables, distinct=False):
    select = "SELECT"
    if distinct:
        select += " DISTINCT"
    
    for variable in variables:
        select += " ?%s" % variable
    
    select += "\n"
    
    return select


def where(*conditions):
    where = "WHERE {"+"\n"
    for cond in conditions
        where += cond+" .\n"
    
    where += "}"+"\n"
    return where

def order_by_asc(variable=None):
    if variable is not None:
        return "ORDER BY ASC(?%s)" % variable
    else:
        return ""


def limit(limit=1000000):
    if type(limit) is int:
        return "LIMIT %i" % limit
    else:
        return ""
