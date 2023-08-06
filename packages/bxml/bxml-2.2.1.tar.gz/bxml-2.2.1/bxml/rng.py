
from .xml import XML

class RNG(XML):
    NS = {
        'a': "http://relaxng.org/ns/compatibility/annotations/1.0", 
        'epub': "http://www.idpf.org/2007/ops", 
        'sch': "http://purl.oclc.org/dsdl/schematron", 
        'html': "http://www.w3.org/1999/xhtml", 
        'r': "http://relaxng.org/ns/structure/1.0", 
        'datatypeLibrary': "http://www.w3.org/2001/XMLSchema-datatypes"
    }
    