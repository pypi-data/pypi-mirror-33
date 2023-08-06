#!/usr/bin/python

#__all__ = ['query', 'autoSuggest', 'getSamples']

import sys
import json
import time
import pprint
import base64

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.Thrift import TProcessor
from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol, TProtocol
try:
    from thrift.protocol import fastbinary
except:
    fastbinary = None

from koverse.thriftgen.ttypes import *
from koverse.thriftgen.queryservice import QueryService
from koverse.thriftgen.usergroup import UserGroupService
from koverse.thriftgen.collection import CollectionService
from koverse.thriftgen.dataflow import DataFlowService
from koverse.thriftgen.resource import ResourceService
from koverse.thriftgen.internal import InternalService
from koverse.thriftgen.security.ttypes import *
from koverse.thriftgen.dataflow.ttypes import *
from koverse.thriftgen.collection.ttypes import *

# TODO: read from a properties / yaml file

USERGROUP_PORT = 12321
QUERY_PORT = 12324
COLLECTION_PORT = 12322
DATAFLOW_PORT = 12320
RESOURCE_PORT = 12327
INTERNAL_PORT = 12331


TVAL_STRING = 1
TVAL_LONG= 2 
TVAL_DOUBLE = 3
TVAL_DATE = 4
TVAL_URL = 5
TVAL_IPADDRESS = 6
TVAL_GEO = 7
TVAL_LIST = 8
TVAL_MAP = 9
TVAL_BYTES = 10
TVAL_BOOLEAN = 11

CLIENT_ID = 'defaultClient'
CLIENT_PASSWORD = 'changeMe'

queryClient = None
ugClient = None
collClient = None
dfClient = None
resClient = None
internalClient = None
auth = None

def setClientCredentials(clientId, password):
    global CLIENT_ID
    global CLIENT_PASSWORD
    
    CLIENT_ID = clientId
    CLIENT_PASSWORD = password
    

def authenticate(token):
    """Authenticate with an API token. Raises exception if authentication fails."""

    global auth
    auth = TAuthInfo()
    auth.clientId = CLIENT_ID
    auth.clientPassword = CLIENT_PASSWORD
    auth.apiTokenId = token

    try:
        return ugClient.authenticateAPIToken(token)
    except e:
        print e._message

def authenticateUser(user, password):
    """Authentication with a username and password. Raises exception if authentication fails."""
    if ugClient is None:
        raise Exception('call connect() first')
        
    decoded = base64.b64decode(password)
    global auth
    auth = TAuthInfo()
    auth.clientId = CLIENT_ID
    auth.clientPassword = CLIENT_PASSWORD
    auth.authenticatorId = 'koverseDefault'
    parameters = {
        'emailAddress': user,
        'password': decoded
    }
    try:
        tUser = ugClient.authenticateUser(auth, None, parameters)
        auth.userId = tUser.id
        auth.externalTokens = []
        auth.externalGroups = []
    except Exception, e:
        print e

def connect(host):
    """Provide a hostname. Host needs to have the koverse thrift server listening on 12320, 12321, 12322, 12324, 12327. Returns nothing. Raises exception if connection fails."""

    global queryClient
    global ugClient
    global collClient
    global dfClient
    global resClient
    global internalClient
    
    transport = TSocket.TSocket(host, QUERY_PORT)
    transport = TTransport.TFramedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    queryClient = QueryService.Client(protocol)
    transport.open()
    
    transport = TSocket.TSocket(host, USERGROUP_PORT)
    transport = TTransport.TFramedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    ugClient = UserGroupService.Client(protocol)
    transport.open()
    
    transport = TSocket.TSocket(host, COLLECTION_PORT)
    transport = TTransport.TFramedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    collClient = CollectionService.Client(protocol)
    transport.open()
    
    transport = TSocket.TSocket(host, DATAFLOW_PORT)
    transport = TTransport.TFramedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    dfClient = DataFlowService.Client(protocol)
    transport.open()
    
    transport = TSocket.TSocket(host, RESOURCE_PORT)
    transport = TTransport.TFramedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    resClient = ResourceService.Client(protocol)
    transport.open()
    
    transport = TSocket.TSocket(host, INTERNAL_PORT)
    transport = TTransport.TFramedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    internalClient = InternalService.Client(protocol)
    transport.open()

# private method
def _convertValue(tval): 
    if tval.type == TVAL_STRING:
        return tval.stringValue
    if tval.type == TVAL_LONG:
        return tval.longValue
    if tval.type == TVAL_DOUBLE:
        return tval.doubleValue
    if tval.type == TVAL_DATE:
        return time.gmtime(tval.longValue)
    if tval.type == TVAL_URL:
        return tval.stringValue
    if tval.type == TVAL_IPADDRESS:
        return tval.stringValue
    if tval.type == TVAL_GEO:
        return tval.geoValue
    if tval.type == TVAL_LIST:
        return tval.listValue
    if tval.type == TVAL_MAP:
        return tval.mapValue
    if tval.type == TVAL_BYTES:
        return tval.bytesValue
    if tval.type == TVAL_BOOLEAN:
        return tval.stringValue == 'true' or tval.stringValue == 'True'
    
# private method
def _populateFields(allValues, pointer):
    tval = allValues[pointer]
    if tval.type == TVAL_LIST:
        return [_populateFields(allValues, inner) for inner in tval.listValue]
    elif tval.type == TVAL_MAP:
        return dict([(inner[0], _populateFields(allValues, inner[1])) for inner in tval.mapValue.items()])
    else:
        return _convertValue(tval)

# private method
def _toDict(rec):
    return _populateFields(rec.allValues, 0)
    
def printRecord(rec):
    pprint.pprint(rec)

def query(clauses, datasets=[], offset=0, limit=10000, fields=[], asArrays=False):
    """Provide a dict as the query, a list of collection names, and optional offset, limit, and list of fields to be returned. Returns a list of record dicts."""
    if collClient is None or queryClient is None:
        raise Exception('call connect() first')
        
    # TODO: change to using objectQueryByName
    ids = [collClient.getCollectionByName(auth, c).id for c in datasets]
    
    q = {
        'query': clauses, 
        'collectionIds': ids, 
        'limit': limit, 
        'offset': offset, 
        'fieldsToReturn': fields,
        'returnValuesAsArraysWithType': asArrays
    }

    results = queryClient.objectQuery(auth, json.dumps(q))
    for ds in results:
        ds.records = map(_toDict, ds.records)
    return results

def luceneQuery(queryString, datasets=[], auths=[], numRecords=1000, offset=0, fields=[]):
    if collClient is None or queryClient is None:
        raise Exception('call connect() first')
    
    # 1:security.TAuthInfo auth, 
    # 2:string query, 
    # 3:list<common.TCollectionId> dataSets, 
    # 4:list<security.TAuthorization> auths, 
    # 5:i32 numRecords, 
    # 6:i64 recordOffset, 
    # 7:list<string> fieldsToReturn, 
    # 8:bool removeByteArrayFieldValues, 
    # 9:i32 maxStringValueLength
    
    # TODO: add thrift method for querying via lucene by dataset name
    ids = [collClient.getCollectionByName(auth, c).id for c in datasets]

    results = queryClient.luceneQuery(auth, queryString, ids, auths, numRecords, offset, fields, False, 0)
    for ds in results:
        ds.records = map(_toDict, ds.records)
    return results

def autoSuggest(term, datasets=[]):
    """Provide a term and a list of collection names. Returns a list of suggested search terms."""
    return queryClient.autoSuggestByName(auth, term, datasets)

def getSamples(dataset, maxRecords=1000, removeByteArrays=False, maxStringLength=0):
    """Provide a collection name and optional max records to return (default 1000). Returns a list of record dicts."""
    coll = collClient.getCollectionByName(auth, dataset)
    
    trecs = collClient.getCollectionSample(auth, coll.id, maxRecords, removeByteArrays, maxStringLength)
    return map(_toDict, trecs)

def listDatasets():
    """Lists all collections visible to this user."""
    return collClient.listCollections(auth)

def getDataset(name):
    """Provide a collection name. Returns a collection object."""
    return collClient.getCollectionByName(auth, name)

def createDataset(name):
    
    # struct TCollection {
    #	1:optional common.TCollectionId id
    #	2:optional string name
    #	3:optional string description
    #	4:optional TIndexingPolicy indexingPolicy
    #	5:optional set<string> tags
    #	6:optional common.TUserId responsibleUserId
    #	7:common.TTimestamp createdTimestamp
    #	8:common.TTimestamp updatedTimestamp
    #	9:common.TTimestamp recordCountUpdatedTimestamp
    #	10:i64 recordCount
    #	11:i64 sizeInBytes
    #	12:TCollectionState state
    #	13:optional list<TCollectionGroupPermission> groupPermissions
    #	14:optional list<TCollectionProvenance> provenance
    #	15:list<common.THadoopJobId> hadoopDeleteJobIds
    #	16:i64 version
    #	17:bool deleted
    #	18:bool disableFieldStats
    #	19:bool disableSampling
    #	20:i64 fieldStatsMinimumExecutionPeriod
    #	21:i64 samplingMinimumExecutionPeriod
    #}
    
    coll = TCollection()
    coll.name = name
    
    indexingPolicy = TIndexingPolicy()
    coll.responsibleUserId = auth.userId
    coll.deleted = False
    coll.disableFieldStats = False
    coll.disableSampling = False
    coll.fieldStatsMinimumExecutionPeriod = 3600
    coll.samplingMinimumExecutionPeriod = 3600
    
    return collClient.createCollection(auth, coll)


#def listSourceTypes():
#    """Returns a list of source types."""
#    return dfClient.listSourceTypeDescriptions(auth)
    
#def getSourceOptions(sourceType):
#    return dfClient.getSourceTypeDescriptionBySourceTypeId(auth)

#class TransformJob(object):
    
#    def __init__(self, j):
#        self.j = j
    
#    def getProgress(self):
#        pass
        
#class Transform(object):
    
#    def __init__(self, t):
#        self.t = t
    
#    def run(self, overrideBlocked=False):
        
#        return TransformJob(dfClient.addTransformJob(auth, self.t.transformId))
    
#    def updateParameters(self, params):
#        for name,value in params.items():
#            self.setParameter(name, value)
            
#        self.t = dfClient.updateTransform(auth, self.t)
        
#    def remove(self):
#        pass
        
#    def getParameters(self):
#        return self.t.parameters
        
#    def setParameter(self, name, value):
#        self.t.parameters[name] = _configValue(value)
    
#    def getJobs(self):
#        pass
    
#def listTransformTypes():
#    return dfClient.getTransformJobTypes(auth)
    
#def getTransformDescription(transformType):    
#    return dfClient.getTransformJobTypeDescriptionByJobTypeId(auth, transformType)

#TRANSFORM_SCHEDULE_AUTOMATIC = "automatic"
#TRANSFORM_SCHEDULE_PERIOD = "periodic"

#TRANSFORM_INPUT_DATA_WINDOW_ALL_DATA = "allData"
#TRANSFORM_INPUT_DATA_WINDOW_LAST_BATCH = "lastBatch"
#TRANSFORM_INPUT_DATA_WINDOW_SLIDING_WINDOW = "slidingWindow"
    	
#def createTransform(ttype, name, inputCollectionNames, outputCollectionName, options):
    
#    inputColls = [collClient.getCollectionByName(auth, c).id for c in inputCollectionNames]
#    outputColl = collClient.getCollectionByName(auth, outputCollectionName).id
    
#    t = TTransform()

#    t.inputDataWindowType='allData'
#    t.inputDataSlidingWindowSizeSeconds=3600
#    t.scheduleType='automatic'
#    t.name=name
    
#    t.parameters = {
#        'outputCollection': TConfigValue(stringValue=outputColl, type=0),
#        'inputCollection': TConfigValue(type=3, stringList=inputColls)
#    }
    
#    for name, value in options.items():
#        t.parameters[name] = _configValue(value)
    
#    t.replaceOutputData=True
#    t.minimumExecutionPeriod=30
#    #t.disabled=False
#    #t.lastUpdatedDate=0
#    #t.creationDate=0
#    t.type=ttype
#    t.backend='MAP_REDUCE'
    
#    return Transform(dfClient.createTransform(auth, t))

#def _configValue(value):
#    if type(value) == str:
#        return TConfigValue(stringValue=value, type=TConfigValueType.STRING)

#    if type(value) == float:
#        return TConfigValue(doubleValue=value, type=TConfigValueType.DOUBLE)

#    if type(value) == int:
#        return TConfigValue(longValue=value, type=TConfigValueType.LONG)
        
#    if type(value) == list:
#        if len(value) == 0 or type(value[0]) == str:
#            return TConfigValue(stringList=value, type=TConfigValueType.STRING_LIST)
#        if type(value[0]) == float:
#            return TConfigValue(doubleList=value, type=TConfigValueType.DOUBLE_LIST)
#        if type(value[0]) == int:
#            return TConfigValue(longList=value, type=TConfigValueType.LONG_LIST)
            
#    raise TypeError('config value of type: ' + type(value) + ' unsupported')

#def listTransforms(ttype='all'):
#    if ttype == 'all':
#        return map(Transform, dfClient.listTransforms(auth))
#    else:
#        return map(Transform, dfClient.getTransformsByType(auth, ttype))

#def getTransform(name):
#    return Transform(dfClient.getTransformByName(auth, name))
    
    
#def importData(sourceType, dataset, options):
#    
#    source = {
#        sourceTypeId: sourceType,
#    	name:"" + Math.random(),
#    	configurationOptions:{
#    		options
#        }
#    }
#    
#    dfClient.createSource(auth, source)

def storeResourceFile(filename, data):
    
    resource = resClient.createResource(auth, filename)
    resClient.appendDataToResource(auth, resource, data)
    return resource.fileName

# private methods used for spark

def getTransformConfig(transformJobId):
    return internalClient.getPySparkTransformJobConfig(auth, transformJobId)

def commitTransformOutput(datasetName, outputPath, transformJobId):
    return internalClient.markPySparkTransformComplete(auth, datasetName, outputPath, transformJobId)

def markTransformFailed(transformJobId, errorMessage):
    return internalClient.markPySparkTransformFailure(auth, transformJobId, errorMessage)
    
def getSparkRDDConf(datasetName):
    
    return collClient.getSparkRDDConf(auth, datasetName)

def getNewSparkJobOutputPath():
    
    return collClient.getNewSparkJobOutputPath(auth)

def addFilesToDataset(datasetName, outputPath):
    
    return collClient.addSparkFilesToCollection(auth, datasetName, outputPath)
    
def cleanupSparkImportDir(importId):
    
    return collClient.cleanupSparkImportDir(auth, importId)


