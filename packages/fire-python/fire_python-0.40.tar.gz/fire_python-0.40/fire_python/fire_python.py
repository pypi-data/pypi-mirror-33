__author__ = 'Aaron Byrd'

import math
from xml.etree import cElementTree as ElementTree
#from lxml import etree as ElementTree
import os
import uuid


class secondaryCodeClass:
    def __init__(self):
        i=0

    def AddSecondaryCode(self,functionlist,_newcode):
        #print 'Adding code'
        #print type(functionlist)
        #print functionlist
        if functionlist is not None:
            for f in functionlist:
                if getattr(_newcode,f) is not None:
                    setattr(self,f,getattr(_newcode,f))

    def test(self):
        print 'This is a test of the secondary code class'



class BaseNodePair:
    def __init__(self):
        self.first = None  # BaseOntNode
        self.second = None  # BaseOntNode
        self.tRef = None  # NodeTriple
        self.myOrder = 1
        return

class NodeTriple:
    def SubName(self):
        return self.Subj.Identifier
    def PredName(self):
        return self.Pred.Identifier
    def ObjName(self):
        return self.Obj.Identifier
    def __init__(self,S,P,O):
        self.Subj=S
        self.Pred=P
        self.Obj=O
        return
    def __str__(self):
        return self.Subj.str()+' '+self.Pred.str()+' '+self.Obj.str()



class TextLog:
    def __init__(self):
        self.text=[]
        self.MirrorToConsole = False
    def theText(self):
        return ''.join('\n',self.text)
    def Add(self,newtext):
        self.text.append(newtext)
        if self.MirrorToConsole:
            print newtext
    def Reset(self):
        self.text = []

class BaseOntNode:
    def __init__(self, ID, rResource, oThing):
        'Constructor for the BaseOntNode'
        #ID is a string, rResource and oThing are both BaseOntNodes

        self.Identifier = ID
        self.myRoot = ''

        self.PrimaryCode = None

        self.bnpList = []
        self.myTripleList = []
        self.isClass = False
        self.subClassOfMeList = []
        self.superClassOfMeList = []
        self.subPropertyOfMeList = []
        self.superPropertyOfMeList = []
        self.InverseOfMeList = []
        self.EqualVersionsOfMeList = []
        self.TypeOfMeList = []
        self.InstanceOfMeList = []
        self.DomainOf = []
        self.RangeOf = []

        self.hasFunction = False
        self.theFunction = None

        self.hasDomain = []
        self.hasRange = []

        self.PredClass = ''
        self.UserClass = ''
        self.tmpSecondary = ''

        self.isSymmetric = False
        self.isTransitive = False
        if rResource is not None:
            self.AddSuperClass(rResource)
        if oThing is not None:
            self.AddSuperClass(oThing)
        return

    def __str__(self):
        return self.Identifier


    def AddBaseNodePair(self, L, R, t, ord):
        'Links the other BaseOntNodes in the triplet'
        #L, R are BaseOntNode, t is a NodeTriple, ord is an int
        # L and R refer the the position of the two in the triple
        # <summary>
        # Adds a pair of base nodes from the triple. For example, "A P B" will add "P" (first) and "B" (second) to "A".
        # </summary>
        # <param name="L"> The left-most pair of the triple, excluding the root node. For the triple "A P B", for base node A the left would be "P", whereas for P or B the left would be "A" </param>
        # <param name="R"> The right-most pair of the triple, excluding the root node. For the triple "A P B", for base node A or P the right would be "B", whereas for B the right would be "P" </param>
        # <param name="t"> A reference to the entire node triple</param>
        # <param name="ord"> The order in the triple of the base node. For the triple "A P B", A is 1, P is 2, and B is 3</param>
        bnp = BaseNodePair()
        bnp.first = L
        bnp.second = R
        bnp.tRef = t
        bnp.myOrder = ord
        self.bnpList.append(bnp)
        return

    def AddTripleReference(self, t): #t is a NodeTriple
        'Adds the triple ref to the list of triple refs that use this BaseOntNot'
        self.myTripleList.append(t)
        return

    def AddSuperClass(self, superClass): #superClass is a BaseOntNode
        'Creates class links for both self and superClass'
        superClass.isClass = True
        if superClass.subClassOfMeList is None:
            superClass.subClassOfMeList = []
        if self.superClassOfMeList is None:
            self.superClassOfMeList = []
        superClass.subClassOfMeList.append(self)
        self.superClassOfMeList.append(superClass)
        return

    def AddSuperProperty(self, superProperty): #superClass is a BaseOntNode
        'Creates property links for both self and superProperty'
        superProperty.isClass = True
        if superProperty.subPropertyOfMeList is None:
            superProperty.subPropertyOfMeList = []
        if self.superPropertyOfMeList is None:
            self.superPropertyOfMeList = []
        superProperty.subClassOfMeList.append(self)
        self.superPropertyOfMeList.append(superProperty)
        return
    def AddInverse(self, inv):
        'links together inverse concepts'
        if self.InverseOfMeList is None:
            self.InverseOfMeList = []
        if not inv in self.InverseOfMeList:
            self.InverseOfMeList.append(inv)
        #I added this section
        if inv.InverseOfMeList is None:
            inv.InverseOfMeList = []
        if not self in inv.InverseOfMeList:
            inv.InverseOfMeList.append(self)
        return

    def AddEquivalent(self, eqv):
        'links together inverse concepts'
        if self.EqualVersionsOfMeList is None:
            self.EqualVersionsOfMeList = []
        if not eqv in self.EqualVersionsOfMeList:
            self.EqualVersionsOfMeList.append(eqv)
        #I added this section
        if eqv.EqualVersionsOfMeList is None:
            eqv.EqualVersionsOfMeList = []
        if not self in eqv.EqualVersionsOfMeList:
            eqv.EqualVersionsOfMeList.append(self)
        return

    def AddType(self,tof):
        if self.TypeOfMeList is None:
            self.TypeOfMeList = []
        if not tof in self.TypeOfMeList:
            self.TypeOfMeList.append(tof)
        return

    def AddInstance(self,tof):
        if self.InstanceOfMeList is None:
            self.InstanceOfMeList = []
        if not tof in self.InstanceOfMeList:
            self.InstanceOfMeList.append(tof)
        self.isClass = True
        return


class NamedNodeSet:
    def __init__(self):
        self.set = {}
        return

    def Intersection(self, list1, list2, result):
        'creates a new set called result based on which individual members belong to both the two sets list1 and list2'
        ans = []
        if self.set.has_key(list1) and self.set.has_key(list2):
            for bon in self.set[list1]:
                if bon in self.set[list2]:
                    ans.append(bon)
        self.set.update({result:ans})
        return len(ans)

    def SetContains(self,setname,nodename):
        if self.set.has_key(setname):
            for bon in self.set[setname]:
                if bon.str() == nodename.str():
                    return True
        return False

    def Union(self,list1,list2,result):
        'joins two sets together, with the result having all the individual members'
        ans = []
        if list1 in self.set.keys():
            for bon in self.set[list1]:
                ans.Append(bon)
        if list2 in self.set.keys():
            for bon in self.set[list2]:
                if not bon in ans:
                    ans.Append(bon)
        self.set.Update(result,ans)
        return len(ans)

    def Difference(self,BigSet,SubtractSet,result):
        ans = []
        if self.set.has_key(SubtractSet):
            if self.set.has_key(BigSet):
                for bon in self.set[BigSet]:
                    if bon not in self.set[SubtractSet]:
                        ans.append(bon)
        else:
            if self.set.has_key(BigSet):
                for bon in self.set[BigSet]:
                    ans.append(bon)
        self.set.update({result:ans})
        return len(ans)

    def Size(self,setname):
        if self.set.has_key(setname):
            return len(self.set[setname])
        else:
            return 0

    def Merge(self, otherResults):
        n=NamedNodeSet()
        n.set.copy(self.set)
        n.set.update(otherResults.set)
        return n

    def Remove(self, setname):
        if self.set.has_key(setname):
            self.set.pop(setname)
            return True
        return False

    def First(self, setname):
        if self.set.has_key(setname) and isinstance(self.set[setname], BaseOntNode):
            return self.set[setname].Identifier # not sure why we have one that is not in a list...
        if self.set.has_key(setname) and isinstance(self.set[setname], list)  and len(self.set[setname])>0:
            return self.set[setname][0].Identifier
        return ''

    def ExistsSet(self, setname):
        return self.set.has_key(setname)

    def ExistsNonEmptySet(self, setname):
        return self.set.has_key(setname) and len(self.set[setname])>0

    def AddToSet(self, setname, concept, theOntology): #setname is the name of the set that is growing. concept is a string, and theOntology is the ontology
        if setname[0]=='?':
            realsetname = setname[1:]
        else:
            realsetname = setname
        if not self.set.has_key(realsetname):
            thelist = []
        else:
            thelist = self.set[realsetname]

        if theOntology.identList.has_key(concept):
            bon = theOntology.identList[concept]
        else:
            bon = BaseOntNode(concept,None,None)
            theOntology.AddConcept(bon)

        if bon not in thelist:
            thelist.append(bon)

        self.set.update({realsetname:thelist})
        return len(thelist)

    def AddExistingSet(self,setname,BONList):
        self.set.update({setname:BONList})
        return

    def IDSet(self):
         return {k:[bon.Identifier for bon in self.set[k]] for k in self.set.keys()}



class OntologyTripleRefs:
    def __init__(self):
        self.curOntList = None # collection of NodeTriples
        self.set = {} # dictionary of collections of node triples
    def AddTriple(self, t):
        """
        :param t: NodeTriple
        :return: None
        """
        if self.curOntList is None:
            self.SetOntologyName("LocalOntology")
        self.curOntList.append(t)
    def SetOntologyName(self,name):
        if name in self.set.keys():
            self.curOntList = set[name]
        else:
            self.curOntList = []
            self.set.append(name,self.curOntList)





import sys, importlib, socket

class FuncOnt:
    def __init__(self,InitialOntologyName=None):
        self.SecondaryCode = secondaryCodeClass()
        self.identList={}
        self.theTripleList=[]
        self.UserFunctions={}
        self.PredFuncList={}
        self.ScripEngine=None # in the C# version this handles wrapping code
        self.NamespaceList=[]
        self.NamedOntologyNodes={}
        self.OntologyNameSet = []
        self.currentOntologyName=''
        self.currentTripleCollection=None
        if InitialOntologyName is not None:
            self.setCurrentOntologyName(InitialOntologyName)
        else:
            self.setCurrentOntologyName('local.rdf')
        self.log = TextLog()
        self.InitializeBasicNodesAndNamespaces()
        self.trimchars = '?+-'

    def setCurrentOntologyName(self,newName):
        self.currentOntologyName=newName
        found=newName in self.OntologyNameSet
        if not found:
            self.OntologyNameSet.append(newName)
            self.NamedOntologyNodes.update({newName:[]})
        self.currentTripleCollection=self.NamedOntologyNodes[newName]

    def MakeTempNamedNodeSet(self):
        return NamedNodeSet()



    def CreateNSMapReverseLookup(self):
        self.nsmap_reverse = {v: k for k, v in self.nsmap.items()}
        return

    def FullyQualifiedName(self,concept):
        if concept[0]!='{' and concept[0]!='[':
            parts = concept.split(":")
            if len(parts)>1:
                if self.nsmap.has_key(parts[0]):
                    return '{0}{1}'.format(self.nsmap[parts[0]],parts[1])
                else:
                    return '{0}{1}'.format('{NAMESPACE_NOT_FOUND}',parts[1])
            else:
                return '{0}{1}'.format(self.nsmap['local'], parts[0])
        else:
            return concept

    def PrettyName(self,concept):
        if concept is not None and len(concept)>0:
            if concept[0]=='{':
                parts=concept.split("}")
                parts[0] = '{0}{1}'.format(parts[0],'}')
                if self.nsmap_reverse.has_key(parts[0]):
                    return '{0}:{1}'.format(self.nsmap_reverse[parts[0]],parts[1])
                else:
                    return concept
        return concept

    def InitializeBasicNodesAndNamespaces(self):
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)

        #LOCAL_NAMESPACE = "http://local.namespace"
        LOCAL = "{http://%s#}" % IP
        RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        RDF = "{%s}" % RDF_NAMESPACE
        RDFS_NAMESPACE = "http://www.w3.org/2000/01/rdf-schema#"
        RDFS = "{%s}" % RDFS_NAMESPACE
        XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema#"
        XSD = "{%s}" % XSD_NAMESPACE
        XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace#"
        XML = "{%s}" % XML_NAMESPACE
        OWL_NAMESPACE = "http://www.w3.org/2002/07/owl#"
        OWL = "{%s}" % OWL_NAMESPACE
        FO_NAMESPACE = "http://hydrology.usu.edu/FunctionalOntology/syntax#"
        FO = "{%s}" % FO_NAMESPACE

        self.nsmap = {'local':LOCAL,
                      'rdf':RDF,
                      'rdfs':RDFS,
                      'xsd':XSD,
                      'xml':XML,
                      'owl':OWL,
                      'fo':FO}
        self.CreateNSMapReverseLookup()

        # Create the root nodes, one for OWL, one for RDF
        self.othing = 'owl:Thing'
        self.othing_node = BaseOntNode(self.othing,None,None)
        self.rresource = 'rdf:Resource'
        self.rresource_node = BaseOntNode(self.rresource,None,None)
        self.identList.update({self.othing:self.othing_node})
        self.identList.update({self.rresource:self.rresource_node})

        conceptList = ['rdf:Description','rdf:Resource','rdfs:Class','rdfs:Literal','rdfs:Datatype',
                       'rdfs:XMLLiteral','rdf:Property','rdfs:range','rdfs:domain','rdf:type',
                       'rdfs:SubClassOf','rdf:subPropertyOf','rdfs:label','rdfs:label',
                       'rdfs:comment','rdfs:Container','rdf:Bag','rdf:Seq','rdf:Alt',
                       'rdfs:member','rdf:List','rdf:first','rdf:rest','rdf:nil','rdf:Statement',
                       'rdfs:subject','rdf:predicate','rdf:object','rdf:seealso','rdf:isDefinedBy',
                       'rdf:value','rdf:about','fo:PrimaryCode','rdf:RDF','owl:InverseOf',
                       'owl:EquivalentClass','owl:EquivalentProperty','owl:SymmetricProperty',
                       'owl:TransitiveProperty','owl:SameAs','owl:Includes']

        for c in conceptList:
            c_lower = c # c.lower()  change this to not be lower case
            c_nocolon = c_lower.replace(':','')
            c_fullyqualifiedname=self.FullyQualifiedName(c_lower)
            setattr(self,c_nocolon,c_lower)
            self.identList.update({c_lower:BaseOntNode(c_lower,self.rresource_node,self.othing_node)})

        return


    def EncodeLiteral(self,value):
        return '['+str(uuid.uuid4())+':'+str(value)+']'

    def DecodeLiteral(self,value):
        removeLast = False
        if value==None:
            return None
        if len(value)==0:
            return value
        if value[-1]==']':
            removeLast = True
        startval = value.find(':')
        if startval==-1:
            return value
        if removeLast:
            return value[startval+1:-1]
        else:
            return value[startval+1:]


    def AddBaseNode(self, ID):
        newNode = BaseOntNode(ID,self.rresource_node,self.othing_node)
        self.identList.update({ID:newNode})
        return newNode

    def AddPredFunction(self,ID,f):
        #print 'Not implemented yet'
        self.identList[ID].PrimaryCode=f
        return
    #def ClearPredFuncList(self):
    #    print 'Not implemented yet'
    #    return

    def AddTriplesFromResults(self, SubjectConcept,PredicateConcept,ObjectConcept,results):
        """
        either subjet, predicate, or object is a name of a set in results. We want to swap in the values in
        the set in the triples to be added.
        :param SubjectConcept:
        :param PredicateConcept:
        :param ObjectConcept:
        :param results:
        :return:
        """
        if SubjectConcept[0]=='+':
            s=self.TrimStart(SubjectConcept)
            if s in results.sets.keys():
                for snew in results.sets[s]:
                    self.AddTriple(snew,PredicateConcept,ObjectConcept)
        if PredicateConcept[0]=='+':
            s=self.TrimStart(PredicateConcept)
            if s in results.sets.keys():
                for snew in results.sets[s]:
                    self.AddTriple(SubjectConcept,snew,ObjectConcept)
        if ObjectConcept[0]=='+':
            s=self.TrimStart(ObjectConcept)
            if s in results.sets.keys():
                for snew in results.sets[s]:
                    self.AddTriple(SubjectConcept,PredicateConcept,snew)

    def AddTriple(self,SubjectConcept, PredicateConcept, ObjectConcept):
        isSubClass = False
        isDomain = False
        isRange = False
        isSubProperty = False
        isInverse = False
        isEquivalent = False
        isTypeOf = False

        if self.AlreadyInList(SubjectConcept):
            S = self.identList[SubjectConcept]
        else:
            S = self.AddBaseNode(SubjectConcept)

        exists_P,P = self.ExistsBON(PredicateConcept)

        if exists_P:
            if self.CompareFullyQualifiedAndEquivalentNames(PredicateConcept,self.rdftype):
                isTypeOf=True
            elif self.CompareFullyQualifiedAndEquivalentNames(PredicateConcept,self.rdfsSubClassOf):
                isSubClass = True
            elif self.CompareFullyQualifiedAndEquivalentNames(PredicateConcept,self.rdfsrange):
                isRange=True
            elif self.CompareFullyQualifiedAndEquivalentNames(PredicateConcept,self.rdfsdomain):
                isDomain=True
            elif self.CompareFullyQualifiedAndEquivalentNames(PredicateConcept,self.owlInverseOf):
                isInverse=True
            elif self.CompareFullyQualifiedAndEquivalentNames(PredicateConcept,self.owlEquivalentProperty):
                isInverse=True
            elif self.CompareFullyQualifiedAndEquivalentNames(PredicateConcept,self.owlEquivalentClass):
                isInverse=True
            elif self.CompareFullyQualifiedAndEquivalentNames(PredicateConcept,self.owlSameAs):
                isInverse=True
        else:
            P = self.AddBaseNode(PredicateConcept)

        exists_O,O=self.ExistsBON(ObjectConcept)
        if not exists_O:
            O = self.AddBaseNode(ObjectConcept)


        #create new triple and add to list
        t = NodeTriple(S, P, O)
        self.NamedOntologyNodes[self.currentOntologyName].append(t)
        self.theTripleList.append(t)

        #set up self-references
        S.AddBaseNodePair(P,O,t,1)
        P.AddBaseNodePair(S,O,t,2)
        O.AddBaseNodePair(S,P,t,3)

        S.AddTripleReference(t)
        P.AddTripleReference(t)
        O.AddTripleReference(t)

        #add the logic
        if S.DomainOf == None:
            S.DomainOf = []
        if O.RangeOf == None:
            O.RangeOf = []

        S.DomainOf.append(P)
        O.RangeOf.append(P)

        if isTypeOf:
            if O==self.GetBON(self.rdfsClass):
                S.isClass=True
            else:
                S.AddType(O)
                O.AddInstance(S)

        if isSubClass:
            S.AddSuperClass(O)
            S.isClass=True
            O.isClass=True

        if isSubProperty:
            S.AddSuperProperty(O)
            if O==self.GetBON(self.owlTransitive):
                P.isTransitive = True
            if O==self.identList(self.owlSymmetric):
                P.isSymmetric = True

        if isDomain:
            if S.hasDomain == None:
                S.hasDomain = []
            S.hasDomain.append(O)
            O.isClass = True

        if isInverse:
            S.AddInverse(O)
            O.AddInverse(S)

        if isEquivalent:
            S.AddEquivalent(O)
            O.AddEquivalent(S)



    def GetBON(self,nodename):
        if nodename in self.identList.keys():
            return self.identList[nodename]
        if nodename.lower() in self.identList.keys():
            return self.identList[nodename.lower()]
        pn = self.PrettyName(nodename)
        if pn in self.identList.keys():
            return self.identList[pn]
        if pn.lower() in self.identList.keys():
            return self.identList[pn.lower()]
        #print 'BON key not found: '+nodename
        return None

    def ExistsBON(self,nodename):
        if nodename in self.identList.keys():
            return True,self.identList[nodename]
        if nodename.lower() in self.identList.keys():
            return True,self.identList[nodename.lower()]
        pn = self.PrettyName(nodename)
        if pn in self.identList.keys():
            return True, self.identList[pn]
        if pn.lower() in self.identList.keys():
            return True, self.identList[pn.lower()]
        return False,None

    def CreateEqualVersionNodeList(self,nodename,ExistingList=None):
        nodenamefq = self.FullyQualifiedName(nodename)
        node=self.GetBON(self.PrettyName(nodenamefq))
        if node == None:
            return ExistingList

        if ExistingList is None:
            ExistingList=[]
        if not node in ExistingList:
            ExistingList.append(node)
        for e in node.EqualVersionsOfMeList:
            if not e in ExistingList:
                ExistingList.append(e)
                self.CreateEqualVersionNodeList(e.Identifier,ExistingList)
        return ExistingList

    def GetEquivalentAndSuperClassNodeList(self,node,ExistingList=None):

        if node == None:
            return []

        if type(node) == str:
            node = self.GetBON(node)
        elif type(node) is not BaseOntNode:
            assert Exception("unknown search parameter")

        if ExistingList==None:
            ExistingList=[]

        firstorderattriblist = ['EqualVersionsOfMeList','superClassOfMeList','superPropertyOfMeList','TypeOfMeList']
        secondorderattriblist_first = ['DomainOf','RangeOf']
        secondorderattriblist_second = ['hasDomain','hasRange']

        if node not in ExistingList:
            ExistingList.append(node)
        else:
            return ExistingList # already searched this node

        for a in firstorderattriblist:
            thelist = getattr(node,a)
            if thelist is not None and len(thelist)>0:
                for n in thelist:
                    if n not in ExistingList:
                        ExistingList=self.GetEquivalentAndSuperClassNodeList(n,ExistingList)
        for a,b in zip(secondorderattriblist_first,secondorderattriblist_second):
            thelist = getattr(node,a)
            if thelist is not None and len(thelist)>0:
                for n in thelist:
                    thesecondlist = getattr(n,b)
                    if thesecondlist is not None and len(thesecondlist)>0:
                        for n2 in thesecondlist:
                            if n2 not in ExistingList:
                                ExistingList = self.GetEquivalentAndSuperClassNodeList(n2,ExistingList)
        return ExistingList



    def GetEquivalentSuperClassInverseNodeList(self,pred):
        """

        :param pred: BaseOntNode
        :return: list of BaseOntNodes
        """
        nodeList = self.GetEquivalentAndSuperClassNodeList(pred)
        invPredList = []
        for p in nodeList:
            if p.InverseOfMeList is not None and len(p.InverseOfMeList)>0:
                for pInv in p.InverseOfMeList:
                    if pInv not in invPredList:
                        invPredList.append(pInv)
        return invPredList



    def CompareFullyQualifiedAndEquivalentNames(self,left,right):
        if left is None or right is None:
            return False
        leftnodelist=self.CreateEqualVersionNodeList(left)
        rightnodelist=self.CreateEqualVersionNodeList(right)

        for r in rightnodelist:
            if r in leftnodelist:
                return True
        return False


    def hasMatchSubSearch(self,primary,matchNode,alreadySearched):
        """
        This method looks for and and all matches to matchNode by anything that is an equal value of primary
        equal value is defined as equivalent to primary or superclass of primary
        superclass of primary can be defined via "subClassOf", "subPropertyOf", "type" "Domain", or "Range" relationships

        :param primary:
        :param matchNode:
        :param alreadySearched: begin with an empty list. Used to keep track through recursive runs
        :return: bool
        """
        retval = False
        firstorderattriblist = ['EqualVersionsOfMeList','superClassOfMeList','superPropertyOfMeList','TypeOfMeList']
        secondorderattriblist_first = ['DomainOf','RangeOf']
        secondorderattriblist_second = ['hasDomain','hasRange']

        alreadySearched.append(primary)
        if matchNode==primary:
            return True
        else:
            for a in firstorderattriblist:
                thelist = getattr(primary,a)
                if thelist is not None and len(thelist)>0:
                    for n in thelist:
                        if n not in alreadySearched:
                            retval = self.hasMatchSubSearch(n,matchNode,alreadySearched)
                            if retval:
                                return True
            for a,b in zip(secondorderattriblist_first,secondorderattriblist_second):
                thelist = getattr(primary,a)
                if thelist is not None and len(thelist)>0:
                    for n in thelist:
                        thesecondlist = getattr(n,b)
                        if thesecondlist is not None and len(thesecondlist)>0:
                            for n2 in thesecondlist:
                                if n2 not in alreadySearched:
                                    retval = self.hasMatchSubSearch(n2,matchNode,alreadySearched)
                                    if retval:
                                        return True
            for bnp in primary.bnpList:
                if bnp.myOrder == 1 and bnp.first==self.identList[self.rdftype]:
                    if bnp not in alreadySearched:
                        retval = self.hasMatchSubSearch(bnp.second,matchNode,alreadySearched)
                        if retval:
                            return True


    def hasMatch(self, primary, matchNode):
        #primary and matchNode are BaseOntNodes
        checkedList1=[]
        checkedList2=[]
        return self.hasMatchSubSearch(primary, matchNode, checkedList1) or self.hasMatchSubSearch(matchNode, primary, checkedList1)

    def FindSubset(self,answerSet, pairList, isFirst, matchNode,baseOrder):
        """

        :param answerSet: set of node triples
        :param pairList: set of base node pairs
        :param isFirst: boolean
        :param matchNode: BaseOntNode
        :param baseOrder: int
        :return: changes answerSet
        """
        if isFirst:
            for bnp in pairList:
                if self.hasMatch(bnp.first, matchNode) and bnp.myOrder == baseOrder:
                    answerSet.append(bnp.tRef)
        else:
            for bnp in pairList:
                if self.hasMatch(bnp.second,matchNode) and bnp.myOrder == baseOrder:
                    answerSet.append(bnp.tRef)

    def GetEquivalentAndSubClassNodeListRecursiveSearch(self,node,thelist):
        if node not in thelist:
            thelist.append(node)
        attribs = ['EqualVersionsOfMeList','subClassOfMeList','superPropertyOfMeList']
        for a in attribs:
            checklist = getattr(node,a)
            if checklist is not None and len(checklist)>0:
                for eqv in checklist:
                    if eqv not in thelist:
                        self.GetEquivalentAndSubClassNodeListRecursiveSearch(eqv,thelist)

    def GetEquivalentAndSubClassNodeList(self, node):
        nodeList = []
        if isinstance(node,BaseOntNode):
            self.GetEquivalentAndSubClassNodeListRecursiveSearch(node,nodeList)
            return nodeList
        elif isinstance(node,list):
            if len(node)> 0:
                if isinstance(node[0], BaseOntNode):
                    firstlist = node
                    for n in firstlist:
                        self.GetEquivalentAndSubClassNodeListRecursiveSearch(n, nodeList)
                    return nodeList
                else:
                    assert Exception("unknown type in GetEquivalentAndSubClassNodeList: "+str(type(node[0])))
            else:
                return []
        else:
            assert Exception("unknown type in GetEquivalentAndSubClassNodeList: "+str(type(node)))
        return

    def DoesNodeHaveClassType(self,theNode,parentType):
        retval = False
        if parentType in theNode.superClassOfMeList:
            return True
        for bon in theNode.superClassOfMeList:
            retval = self.DoesNodeHaveClassType(bon,parentType)
            if retval:
                return True

        return retval


    def ClassSearch(self,rootnode,results):
        """
        Search for the class of a node
        :param rootnode: the BaseOntNode of the term
        :param results: an array
        :return:
        """
        alreadychecked = []
        self.RecursiveClassSearch(rootnode,results,alreadychecked,rootnode,True)

    def RecursiveClassSearch(self,curnode,results,alreadyChecked,rootnode,DontAddToList):
        attrlist = ['superClassOfMeList','superPropertyOfMeList','EqualVersionsOfMeList','TypeOfMeList']
        if curnode not in alreadyChecked:
            if not DontAddToList and not curnode in results:
                results.append(curnode)
            alreadyChecked.append(curnode)

            #loop through the defined lists above
            for a in attrlist:
                a_list = getattr(curnode,a)
                if a_list is not None and len(a_list)>0:
                    for sup in a_list:
                        self.RecursiveClassSearch(sup,results,alreadyChecked,rootnode,False)

            # do domain and range searches
            if curnode.hasDomain is not None and len(curnode.hasDomain)>0:
                for dmOf in curnode.DomainOf:
                    if dmOf.hasDomain is not None and len(dmOf.hasDomain)>0:
                        for bonDm in dmOf.hasDomain:
                            self.RecursiveClassSearch(bonDm,results,alreadyChecked,rootnode,False)
                    if dmOf.InverseOfMeList is not None and len(dmOf.InverseOfMeList)>0:
                        for bonInv in dmOf.InversOfMeList:
                            if bonInv.hasRange is not None and len(bonInv.hasRange)>0:
                                for bonRg in bonInv.hasRange:
                                    self.RecursiveClassSearch(bonRg,results,alreadyChecked,rootnode,False)
            if curnode.RangeOf is not None and len(curnode.RangeOf)>0:
                for rgOf in curnode.RangeOf:
                    if rgOf.hasRange is not None and len(rgOf.hasRange)>0:
                        for bonRg in rgOf.hasRange:
                            self.RecursiveClassSearch(bonRg,results,alreadyChecked,rootnode,False)
                    if rgOf.InverseOfMeList is not None and len(rgOf.InverseOfMeList)>0:
                        for bonInv in rgOf.InverseOfMeList:
                            if bonInv.hasDomain is not None and len(bonInv.hasDomain)>0:
                                for bonDm in bonInv.hasDomain:
                                    self.RecursiveClassSearch(bonDm,results,alreadyChecked,rootnode,False)


    def AddPredToList(self, predlist, pred, myorder,orderdict):
        """

        :param predlist: list of BaseOntNode
        :param pred: BaseOntNode
        :param myorder: int
        :param orderdict: dictionary: {BaseOntNode:int}
        :return:
        """
        if pred in orderdict.keys():
            curval = orderdict[pred]
            orderdict[pred] = curval | myorder #bitwise or
            return
        else:
            orderdict.update({pred:myorder})

        oppositeflag = orderdict[pred]
        if oppositeflag == 1 or oppositeflag ==2:
            oppositeflag = 1 - (oppositeflag - 2)

        predlist.append(pred)

        attriblist = ['subClassOfMeList','subPropertyOfMeList','EqualVersionsOfMeList','InverseOfMeList']
        orderlist = [myorder,myorder,myorder,oppositeflag]

        for a,o in zip(attriblist,orderlist):
            a_list = getattr(pred,a)
            if a_list is not None and len(a_list) > 0:
                for bon in a_list:
                    self.AddPredToList(predlist,bon,o,orderdict)

    def FindObjMatch(self,O):
        """

        :param O: BaseOntNode
        :return: list of BaseOntNodes
        """

        predlist = []
        orderdict = {}
        eqvO = self.GetEquivalentAndSubClassNodeList(O)
        results = []

        for tO in eqvO:
            for bnp in tO.bnpList:
                if bnp.myOrder == 3: # don't care about 1 or 2
                    if bnp.second == self.identList[self.rdfsdomain]:
                        self.AddPredToList(predlist,bnp.first,1,orderdict)
                    if bnp.second == self.identList[self.rdfsrange]:
                        self.AddPredToList(predlist,bnp.first,2,orderdict)
        for P in predlist:
            if orderdict[P] & 1 == 1:
                for bnp in P.bnpList:
                    if bnp.myOrder == 2 and not bnp.first in results:
                        results.append(bnp.first)
            if orderdict[P] & 2 == 2:
                for bnp in P.bnpList:
                    if bnp.myOrder==2 and bnp.second not in results:
                        results.append(bnp.second)

        Ptype = self.identList[self.rdftype]
        for bnp in Ptype.bnpList:
            if bnp.myOrder==2 and bnp.second in eqvO and not bnp.first in results:
                results.append(bnp.first)

        return results




    def AlreadyInList(self,name):
        if name in self.identList.keys():
            return True
        return False
    def TrimStart(self,name):
        n=name
        for c in self.trimchars: n = n.lstrip(c)
        return n

    def DoTypeSearch(self,Sub,Pred,Obj,results):
        matchS = False
        matchO=False
        eqvSubList = None
        eqvObjList = None
        S=None #BaseOntNode
        O=None #BaseOntNode
        numGood = 0
        subName = ''
        objName = ''

        if Sub[0] is not '?':
            matchS = True
            if not self.AlreadyInList(Sub):
                return 0
            else:
                S = self.identList[Sub]
                eqvSubList = self.GetEquivalentAndSuperClassNodeList(S.Identifier)
                numGood = numGood + 1
        else: #Sub starts with '?'. Set up to create a named set of base ont nodes
            subName = self.TrimStart(Sub)
            if len(subName) == 0:
                return -1
            if subName in results.set.keys():
                results.set.Remove(subName)

        if Obj[0] is not '?':
            matchO = True
            if not self.AlreadyInList(Obj):
                return 0
            else:
                O = self.identList[Obj]
                eqvObjList = self.GetEquivalentAndSuperClassNodeList(O)
                numGood = numGood + 1
        else:
            # Obj[0]=='?'
            objName = self.TrimStart(Obj)
            if len(objName)==0:
                return -3
            if objName in results.set.keys():
                results.set.Remove(objName)

        if (matchS and matchO):
            # truth test
            newset = []
            for bonS in eqvSubList:
                self.ClassSearch(bonS,newset)
            for testO in newset:
                if testO == O:
                    return 1
            return 0
        elif matchO:
            newset = self.FindObjMatch(O)
            results.set.update({subName:newset})
            return len(newset)
        elif matchS:
            newset = []
            for bonS in eqvSubList:
                self.ClassSearch(bonS,newset)
            results.set.update({objName:newset})
            return len(newset)
        else:
            # they want the type of everything. Not gonna happen.
            return 0


    #FindStandardMatchingSet from the original code
    def ReasoningEngineQuery(self,Sub,Pred,Obj,results):
        #print "You asked {0}, {1}, {2}".format(Sub,Pred,Obj)
        matchS = False
        matchP = False
        matchO = False
        theSet = [] # NodeTriples
        theInvSet = []  # NodeTriples
        subList = []
        predList = []
        objList = []
        eqvSubList = []
        eqvPredList = []
        eqvObjList = []
        eqvInvPredList = []
        countNode = 0
        forceFuncCall = False
        forceFuncNoCall = False
        S=None
        P=None
        O=None
        numGood=0
        subName = 's'
        predName = 'p'
        objName = 'o'
        trimchars = ['?', '-', '+']
        test_force_eval=False
        #print 'Performing search for <{0}> <{1}> <{2}>.'.format(Sub, Pred, Obj)

        if len(Sub) == 0 or len(Pred) == 0 or len(Obj) == 0:
            return 0
        # type search
        if Pred[0] != '?' and Pred[0] != '-' and Sub[0] != '?' and Obj[0] != '?':
            if not self.AlreadyInList(Sub) or not self.AlreadyInList(Obj):
                test_force_eval = True
        if Pred[0] == '-':
            forceFuncNoCall = True
            Prep=self.TrimStart(Pred)
        if Pred[0] == '+' or test_force_eval:
            Pred=self.TrimStart(Pred)
            if not self.AlreadyInList(Pred):
                return 0
            else:
                P=self.GetBON(Pred)
                """
                get the function to execute P, using Sub, Pred, Obj, self, results
                Do a try/catch to catch errors
                return the result of the function call
                if you can't find the function, return 0
                """
                #call the code!!! -ARB
                if P.PrimaryCode is not None:
                    return P.PrimaryCode(Sub,Pred,Obj,results,self)
                return 0 # can't execute function

        # Figure out what we need to do as far as matching goes
        if Pred[0]!='?': # the predicate is given
            matchP=True
            if not self.AlreadyInList(Pred):
                return 0 # not going to be able to match anything not in the list
            else:
                P=self.GetBON(Pred)
                if self.CompareFullyQualifiedAndEquivalentNames(P.Identifier,self.rdftype):
                    return self.DoTypeSearch(Sub, P, Obj, results)
                eqvPredList = self.GetEquivalentAndSuperClassNodeList(P.Identifier)
                eqvInvPredList = self.GetEquivalentSuperClassInverseNodeList(P.Identifier)
                numGood = numGood + 1
        else:
            # set up to create a named set of base nodes
            predName=self.TrimStart(Pred)
            if len(predName)==0:
                return -2
            if predName in results.set.keys():
                results.set.Remove(predName)

        if Sub[0] != '?':
            matchS=True
            if not self.AlreadyInList(Sub):
                return 0
            else:
                S=self.GetBON(Sub)
                eqvSubList = self.GetEquivalentAndSuperClassNodeList(S.Identifier)
                numGood = numGood + 1
        else:
            subName = self.TrimStart(Sub)
            if len(subName) == 0:
                return -1
            if subName in results.set.keys():
                results.set.Remove(subName)

        if Obj[0]!='?':
            matchO = True
            if not self.AlreadyInList(Obj):
                return 0
            else:
                O = self.GetBON(Obj)
                eqvObjList = self.GetEquivalentAndSuperClassNodeList(O.Identifier)
                numGood = numGood + 1
        else:
            objName = self.TrimStart(Obj)
            if len(objName)==0:
                return -3
            if objName in results.set.keys():
                del results.set[objName]

        # Now perform the query
        if numGood == 0: # query (?s, ?p, ?o)
            return -4 # I'm just gonna say it now, you're an idiot.

        if numGood == 1: # query (?s, ?p, 0), (?s, p,?o), or (s, ?p, ?o)
            return -5 #you may want the list of everything that matches your concept, but I'm not coding this now.

        if numGood > 1 :
            if matchS:
                if matchP:
                    #(S, P, ?O) or (S, P, O)
                    #forward search
                    for bS in eqvSubList:
                        self.FindSubset(theSet,bS.bnpList,True, P, 1)
                    #inverse search
                    for bP in eqvInvPredList:
                        self.FindSubset(theInvSet,bP.bnpList,False, S, 2)

                    if len(theSet)> 0 or len(theInvSet) > 0:
                        if matchO: #check all three to see if it is part of the set -> (S, P, O)
                            for nT in theSet:
                                if self.hasMatch(nT.Obj,O):
                                    return 1 #Truth Test
                            for nT in theInvSet:
                                if self.hasMatch(nT.Subj,O):
                                    return 1 # inverse truth test
                            # we didn't find a match
                            return 0
                        #else we are not matching all three, so create the object named set
                        #(S, P, ?O)
                        objList = [nT.Obj for nT in theSet]+[nT.Subj for nT in theInvSet]
                        countNode = len(objList)
                        newObjList = self.GetEquivalentAndSubClassNodeList(objList)
                        if newObjList is not None and len(newObjList)>0:
                            results.set.update({objName:newObjList})
                            return len(newObjList)
                        else:
                            return 0
                    elif not forceFuncNoCall:
                        #couldn't find a match, so try to make a function call
                        bP=self.GetBON(Pred)
                        if bP is not None and bP.PrimaryCode is not None:
                            return bP.PrimaryCode(Sub, Pred, Obj, results, self)
                    return 0 #nothing to return
                else:
                    #(S, ?P, O)
                    # crete a named predicate set
                    for bS in eqvSubList:
                        self.FindSubset(theSet,bS.bnpList, False, 0, 1)
                    for bS in eqvSubList:
                        self.FindSubset(theInvSet, bS.bnpList, True, 0, 1)

                    # not entirely sure this does what I meant it to do, given that I obliterate the results ...
                    doneadd = False
                    for bon in eqvSubList:
                        if not doneadd and self.hasMatch(bon,O):
                            predList.append(self.identList[self.rdftype])
                            doneadd = True

                    # ... right here
                    #predList=[]
                    # so I commented it out.

                    for nT in theSet:
                        predList.append(nT.Pred)

                    Pprime = None
                    for nt in theInvSet:
                        Pprime = self.GetEquivalentSuperClassInverseNodeList(nt.Pred)
                        if len(Pprime) > 0:
                            for pp in Pprime:
                                predList.append(pp)

                    newPredList = self.GetEquivalentAndSubClassNodeList(predList)
                    results.set.update({predName:newPredList})
                    return len(newPredList)
            else:
                # (?S, P, O)
                for bO in eqvObjList:
                    self.FindSubset(theSet,bO.bnpList,False,P,3)
                for bP in eqvInvPredList:
                    self.FindSubset(theInvSet, bP.bnpList,True, O, 2)

                if len(theSet)>0 or len(theInvSet)>0:
                    subList = []
                    for nT in theSet:
                        subList.append(nT.Subj)
                    for nT in theInvSet:
                        subList.append(nT.Obj)
                    newSubList=self.GetEquivalentAndSubClassNodeList(subList)
                    results.set[subName]=newSubList
                    return len(newSubList)
                elif not forceFuncCall:
                    bP = self.GetBON(Pred)
                    if bP is not None and bP.PrimaryCode is not None:
                        return bP.PrimaryCode(Sub, Pred, Obj, results, self)
                return 0














######## Keep Going Here



                ##########################################
    def GetOntologyPackageFiles(self, pkgfolder, pkgname):
        newname=os.path.join(pkgfolder,pkgname)
        if newname not in sys.path:
            sys.path.append(newname)
        modulename = pkgname
        #print sys.path
        #_newcode = __import__(modulename, globals(), locals(), [], 0)
        _newcode = importlib.import_module(modulename)
        # print dir(_newcode)
        if hasattr(_newcode, 'OntologyFileList'):
            rdfList = getattr(_newcode, 'OntologyFileList')
        else:
            rdfList = None
        if hasattr(_newcode, 'InternalOntology'):
            internalOntology = getattr(_newcode,'InternalOntology')
        else:
            internalOntology=None
        if hasattr(_newcode,'SecondaryCodeFunctions'):
            scl_func = getattr(_newcode,'SecondaryCodeFunctions')
            secondaryCodeList = scl_func()
        else:
            secondaryCodeList = None
        print 'Reading ontology: '+pkgname
        if rdfList is not None:
            flist = rdfList()
            filelist = [os.path.join(newname,pkgname,fn) for fn in flist]
            if len(filelist)>0:
                print 'Files: '+', '.join(filelist)
            else:
                print 'No files found.'
        else:
            filelist = []
        if internalOntology is not None:
            iOntology = internalOntology()
            if 'N3' in iOntology.keys():
                print 'Found {0} triples in the internal ontology set of {1}.'.format(len(iOntology['N3']),pkgname)
        else:
            iOntology = {}
        return filelist,iOntology,secondaryCodeList,_newcode

    def GetOntologyModuleFiles(self,mdlFolder,mdlName):
        if mdlFolder not in sys.path:
            sys.path.append(mdlFolder)
        modulename = mdlName
        #print sys.path
        #_newcode = __import__(modulename, globals(), locals(), [], 0)
        _newcode = __import__(modulename[:-3])
        # print dir(_newcode)
        if hasattr(_newcode, 'OntologyFileList'):
            rdfList = getattr(_newcode, 'OntologyFileList')
        else:
            rdfList = None
        if hasattr(_newcode, 'InternalOntology'):
            internalOntology = getattr(_newcode,'InternalOntology')
        else:
            internalOntology=None
        if hasattr(_newcode,'SecondaryCodeFunctions'):
            scl_func = getattr(_newcode,'SecondaryCodeFunctions')
            secondaryCodeList = scl_func()
        else:
            secondaryCodeList = None
        print 'Reading ontology: '+mdlName
        if rdfList is not None:
            flist = rdfList()
            filelist = [os.path.join(mdlFolder,fn) for fn in flist]
            if len(filelist)>0:
                print 'Files: '+', '.join(filelist)
            else:
                print 'No files found.'
        else:
            filelist = []
        if internalOntology is not None:
            iOntology = internalOntology()
            if 'N3' in iOntology.keys():
                print 'Found {0} triples in the internal ontology set of {1}.'.format(len(iOntology['N3']),mdlName)
        else:
            iOntology = {}
        return filelist,iOntology,secondaryCodeList,_newcode

    def ReadOntologyPackageOrModule(self, pkgfolder, pkgname):
        if os.path.isfile(os.path.join(pkgfolder,pkgname)) and '.py' in pkgname[-3:]:
            filelist, internalOntology, secondaryCodeList, _newcode = self.GetOntologyModuleFiles(pkgfolder, pkgname)
        else:
            filelist,internalOntology,secondaryCodeList, _newcode = self.GetOntologyPackageFiles(pkgfolder,pkgname)
        for f in filelist:
            # print f
            if f[-3:].tolower() =='rdf':
                self.ReadXML(f)
            elif f[-3:].tolower() == 'n3e':
                self.ReadN3ERDC(f)
        if internalOntology is not None:
            for ns in internalOntology['Namespace'].keys():
                self.AddNamespace(ns,internalOntology['Namespace'][ns])
            for s,p,o in internalOntology['N3']:
                self.AddTriple(s,p,o)
                if 'fo:PrimaryCode' in p:
                    s_node=self.GetBON(s)
                    self.AddPredFunction(s,getattr(_newcode,o))
                    #s_node.PrimaryCode=getattr(_newcode,o)
        if secondaryCodeList is not None:
            self.SecondaryCode.AddSecondaryCode(secondaryCodeList,_newcode)
        return _newcode




    def ReadN3ERDC(self,filename):
        isNamespace = False
        with open(filename,'r') as fp:
            for line in fp:
                line = fp.readline()
                if line[:9]=='NAMESPACE':
                    isNamespace = True
                    continue
                if line[:10]=='STATEMENTS':
                    isNamespace = False
                    continue
                parts = line.split('\t')
                if isNamespace:
                    if len(parts)>=2:
                        ont.AddNamespace(parts[0],parts[1])
                if not isNamespace:
                    if len(parts)>=3:
                        ont.AddTriple(parts[0],parts[1],parts[2])






    def ReadXML(self,filename):
        import copy
        tree = ElementTree.parse(filename)
        root=tree.getroot()
        #print 'Root',root
        #print 'Root Attributes:',root.attrib
        #print 'Root Namespaces:',root.nsmap
        newnsmap = copy.copy(root.nsmap)

        goodnsmap = {k:'{0}{1}{2}'.format(r'{',newnsmap[k],r'}') for k in newnsmap.keys()}
        #for k in newnsmap.keys():
        #    newnsmap[k] = '{0}{1}{2}'.format('{',newnsmap[k],'}')

        self.nsmap.update(goodnsmap)
        self.CreateNSMapReverseLookup()

        for node in root:
            is_Description = (node.tag.lower() == self.rdfdescription.lower())
            #theSubject = self.FullyQualifiedName(node.attrib[self.rdfabout])
            # print node.attrib
            # print self.FullyQualifiedName(self.rdfabout)
            theSubject = node.attrib[self.FullyQualifiedName(self.rdfabout)]
            for c in node:
                thePredicate = c.tag #self.FullyQualifiedName(c.tag)
                theObject = c.text #self.FullyQualifiedName(c.text)
                #print '{0} {1} {2}'.format(self.PrettyName(theSubject),self.PrettyName(thePredicate),self.PrettyName(theObject))
                #print '{0} {1} {2}'.format(theSubject, thePredicate,theObject)
                if is_Description:
                    self.AddTripleDescription(theSubject,thePredicate,theObject)
                else:
                    self.AddTripleProperty(theSubject,thePredicate,theObject)
            #print 'Node Attributes:',node.attrib
            #print 'Node Tag:',node.tag
            #for childnode in node:
            #    print 'Child Node Tag',childnode.tag
            #    print 'Child Node Text',childnode.text
        return

    def AddTripleDescription(self,theSubject,thePredicate,theObject):
        #print 'D:Adding {0} {1} {2}'.format(self.PrettyName(theSubject), self.PrettyName(thePredicate),
        #                           self.PrettyName(theObject))
        ont.AddTriple(self.PrettyName(theSubject), self.PrettyName(thePredicate),
                                   self.PrettyName(theObject))
        return
    def AddTripleProperty(self,theSubject,thePredicate,theObject):
        #print 'P:Adding {0} {1} {2}'.format(self.PrettyName(theSubject), self.PrettyName(thePredicate),
        #                           self.PrettyName(theObject))
        ont.AddTriple(self.PrettyName(theSubject), self.PrettyName(thePredicate),
                                   self.PrettyName(theObject))
        return

    def AddNamespace(self,shortver,url):
        self.nsmap[shortver]="{%s}" % url
        self.CreateNSMapReverseLookup()




















def createTestFile(fname,functionname):
    f = open(fname,'w')
    f.write('def '+functionname+'():\n')
    f.write('    print "Hello, this is a test of the '+functionname+' function"\n')
    f.write('    return\n')
    f.close()


def TestOntNames(ont):
    print 'Fully Qualified Name Test'
    print ont.FullyQualifiedName('rdfs:Class')
    print ont.FullyQualifiedName('local:test')
    print ont.FullyQualifiedName('fo:PrimaryCode')
    print ont.FullyQualifiedName('nyd:TestNotYetDefined')
    print ont.FullyQualifiedName('[kei495:LiteralValueHere]')
    print '\n'
    print 'Pretty Name Test'
    print ont.PrettyName(ont.FullyQualifiedName('rdfs:Class'))
    print ont.PrettyName(ont.FullyQualifiedName('local:test'))
    print ont.PrettyName(ont.FullyQualifiedName('fo:PrimaryCode'))
    print ont.PrettyName(ont.FullyQualifiedName('nyd:TestNotYetDefined'))
    print ont.PrettyName(ont.FullyQualifiedName('[kei495:LiteralValueHere]'))

    return

def TestOnt(ont):
    #TestOntNames(ont)
    results = ont.MakeTempNamedNodeSet()
    ont.AddTriple('fo:A','rdf:type','rdfs:Class')
    ont.AddTriple('fo:A','fo:hasthing','fo:athing')
    ont.AddTriple('fo:B','rdf:type','fo:A')
    print 'Q1=',ont.ReasoningEngineQuery('fo:B','fo:hasthing','?thething',results)

    print 'Q2=',ont.ReasoningEngineQuery('fo:B','rdf:type','?B_Types',results)
    print results.IDSet()
    return

def GlobalPortOnt(ont):
    #TestOntNames(ont)
    results = ont.MakeTempNamedNodeSet()
    
    ont.AddNamespace('port','https://umip.erdc.dren.mil/port/ontology#')

    # example of global triples
    ont.AddTriple('port:Port','rdf:type','rdfs:Class')
    
    #ont.AddTriple('port:hasAttribute:','rdf:type','rdf:Property')
    ont.AddTriple('port:hasPort_Key','rdfs:domain','port:Port')
    ont.AddTriple('port:hasHARBORSIZE','rdfs:domain','port:Port')
    ont.AddTriple('port:hasHARBORTYPE','rdfs:domain','port:Port')
    ont.AddTriple('port:hasCHAN_DEPTH','rdfs:domain','port:Port')
    
    ont.AddTriple('port:hasPort_Key','rdfs:range','port:Port_KeyString')
    ont.AddTriple('port:hasHARBORTYPE','rdfs:range','port:HARBORTYPEString')
    ont.AddTriple('port:hasHARBORSIZE','rdfs:range','port:HARBORSIZEString')
    ont.AddTriple('port:hasCHAN_DEPTH','rdfs:range','port:CHAN_DEPTHString')
    
    ont.AddTriple('port:Port_KeyString','rdfs:subClassOf','xml:string')
    ont.AddTriple('port:HARBORTYPEString','rdfs:subClassOf','xml:string')
    ont.AddTriple('port:HARBORSIZEString','rdfs:subClassOf','xml:string')
    ont.AddTriple('port:CHAN_DEPTHString','rdfs:subClassOf','xml:string')

    #ont.AddTriple('port:hasCHAN_DEPTH:','rdf:type','rdf:Property')
    #ont.AddTriple('port:hasHARBORSIZE:','rdf:type','rdf:Property')


    # example of local triples
    ont.AddTriple('port:PortA','rdf:type','port:Port')
    ont.AddTriple('port:PortA','port:hasCHAN_DEPTH','port:DepthRange3To15')
    #ont.AddTriple('port:PortB','rdf:type','port:Port')
    ont.AddTriple('port:PortB','port:hasCHAN_DEPTH','port:DepthRange14To37')

    print 'Q1=',ont.ReasoningEngineQuery('port:PortB','port:hasCHAN_DEPTH','?CHAN_DEPTH',results)
    print 'Q2=',ont.ReasoningEngineQuery('port:PortA','rdf:type','?Port_Type',results)
    print 'Q3=',ont.ReasoningEngineQuery('?AllChanDepths','rdf:type','port:CHAN_DEPTHString',results)

    print results.IDSet()
    return
#from testcode.trial import helloworld


def testSCD(ont):
    _newcode=ont.ReadOntologyPackageOrModule('C:\\work\\fire_rdf\\ship_class_data','ship_class_data')
    b=ont.GetBON('scd:hasLength')
    b.PrimaryCode('a','b','c','d',ont)
    results = ont.MakeTempNamedNodeSet()
    ont.ReasoningEngineQuery('?allships','rdf:type','scd:ShipClass',results)
    ont.SecondaryCode.test()
    if 'allships' in results.set.keys():
        for s in results.set['allships']:
            labelname = s.Identifier.replace(':','_')+'label'
            ont.ReasoningEngineQuery(s.Identifier,'rdfs:label','?'+labelname,results)
            if labelname in results.set.keys():
              print ont.DecodeLiteral(results.First(labelname))

if __name__ == '__main__':
    #print "This only executes when %s is executed rather than imported" % __file__

    #ont=Ontology()
    #ont.ReadFile("testdata/port_v1.csv")
    #ont.ReasoningEngineQuery("?", "is_a","Port")

    # modulepath = 'C:\\work\\fire_rdf'
    # modulename = 'testrdf'
    ont=FuncOnt()
    testSCD(ont) #GlobalPortOnt(ont)
    exit(0)

    # ont.ReadOntologyPackage(modulepath,modulename)


    # newfilename = 'fo_primarycode'
    # newfilename_py = newfilename+'.py'
    # functionname = 'awesomefunction'

    # fullfilename=os.path.join(modulepath,newfilename_py)
    # modulename = modulepath+'.'+newfilename
    #createTestFile(fullfilename,functionname)
    #_newcode = __import__(modulename, globals(), locals(), [functionname], 0)
    #print globals
    #my_function = getattr(_newcode, functionname)
    #my_function()



    #helloworld()


    #my_other_function = getattr(views, 'my_other_function')
    #my_attribute = getattr(views, 'my_attribute')