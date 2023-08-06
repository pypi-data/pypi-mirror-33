=========
FIRE-PYTHON README
=========

FIRE - Python stands for "FunctIonal Reasoning Engine - Python". Fire-Python is a python implementation of the
Functional Ontologies developed by Aaron Byrd for his Ph.D. dissertation.

Functional Ontologies and Their Application to Hydrologic Modeling: Development of an Integrated Semantic and Procedural Knowledge Model and Reasoning Engine

Unlike C#, there are several niceties in Python that simplify much of the behind-the-scenes gruntwork of making the code
and the deductive logic engine play well together.


Creating Python Functional Ontologies
=====================================

Currently, the easiest way to make a functional ontology for Fire-Python is to make a python file like the following:


```
def OntologyFileList():
    return []

def InternalOntology():
    o={}
    o['Namespace']={
        'scd':'http://umip.erdc.dren.mil/ontologies/shipclassdata#',
                    }
    o['N3']=[
        ('scd:ShipClass', 'rdf:type', 'rdfs:Class'),
        ('scd:hasShipClassLabel', 'rdf:type', 'rdf:Property'),
        ('scd:hasShipClassLabel', 'rdf:range', 'scd:ShipClassLabel'),
        ('scd:hasShipCode', 'rdf:type', 'rdf:Property'),
        ('scd:hasShipCode', 'rdf:range', 'scd:ShipCode'),
        ('scd:shipLength_ft', 'rdf:range', 'units:feet'),
        ('scd:shipBeam_ft', 'rdf:range', 'units:feet'),
        ('scd:shipDisplacement_tons', 'rdf:range', 'units:tons'),
        ('scd:hasTestValue','fo:PrimaryCode','scdHasTestValue')
    ]

def scdHasTestValue(Subj,Pred,Obj,Results,FO):
    """
    Subj is the Subject - string
    Pred is the predicate. In this case it is "scd:hasTestValue" - string
    Obj is the Object - string
    Results is an instance of the class NamedNodeSet
    FO is an instance of the class FuncOnt

    return value is the number of nodes added to the results set. 0 would mean no value was returned.
    """
    if Subj[0]=='?' and Obj[0]!='?':
        # question is "what hasTestValue X"
        return 0
    if Subj[0]!='?' and Obj[0]=='?':
        # question is "Thing hasTestValue what"
        return 0
    if Subj[0]=='?' and Obj[0]=='?':
        # question is "what hasTestValue what"
        return 0
    if Subj[0]!='?' and Obj[0]!='?':
        # question is a truth test: "Does Thing haveTestValue X"
        # return 1 for True, 0 for False
        return 0
    return 0

```

Expected Functions
------------------------

The two expected functions are OntologyFileList and InternalOntology. The OntologyFileList function should return
a list of bare ontology files, either in RDF or N3 format.

The InternalOntology function should return a dictionary with the keys 'Namespace' and 'N3'.

Ontology Organization
-------------------------
The 'Namespace' member of the dictionary should be a dictionary with a list of namespaces in the format of: ::

'shorthand':'Full URL'

The 'N3' member of the dictionary should be a list of tuple triplets. These tuple triplets are simple sentences that
form the basis of the ontology. The tuples triplets are of the form: ::

(Subject,Predicate,Object)

Each entry needs to refer to a uniquely identifiable concept, and thus the use of namespaces with URLs. The namespace
URLs don't actually need to exist, they just need to be unique. It would be helpful if they actually existed as tags on an
HTML document, though. Then they can be commented for usability.

To add functionality to your ontology, use the predicate fo:PrimaryCode. This indicates that there is a function (whose
name is the object) that can be called if the reasoning engine cannot deduce the request concept. The purpose of the function
is to answer the request. Thus, it needs to end up adding nodes to the results set as necessary. It should return the number of
nodes it added to the results. Given that purpose, though, the function is free to do whatever you want. The only limitations
are the packages you have installed and the limitations you have placed on python. It could do more queries to find out more information.
It could run a web service. It could read from a file. It could ask the user for input. It could run another program.

The scdHasTestValue function shows the basic skeleton of a primary code function.





