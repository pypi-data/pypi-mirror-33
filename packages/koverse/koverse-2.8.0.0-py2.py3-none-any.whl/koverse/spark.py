
from pyspark import *
from koverse import client

class KoverseSparkContext(object):
    """
    """
    
    def __init__(self, sparkContext, hostname, username, password):
        
        self.sparkContext = sparkContext
        client.connect(hostname)
        client.authenticateUser(username, password)
        
        
    def koverseDataset(self, datasetName):
        
        try :
            conf = client.getSparkRDDConf(datasetName)
        except Exception, e:
            print 'got error: ' + str('unauthorized')
            return
        
        rdd = self.sparkContext.newAPIHadoopRDD(
            'com.koverse.mapreduce.KoverseInputFormat',
            'org.apache.hadoop.io.Text',
            'java.util.HashMap',
            conf = conf)
        
        # present only the value of the key-value pair
        rdd = rdd.map(lambda r: r[1])
        
        # store the conf with the rdd
        return rdd

        
    def saveAsKoverseDataset(self, rdd, datasetName, append=False):
        
        # try to create the collection if it doesn't exist
        colls = client.listDatasets()

        if datasetName in [c.name for c in colls]:
            if not append:
                raise Exception('collection already exists and append set to false')
            coll = client.getDataset(datasetName)
        else:
            coll = client.createDataset(datasetName)
            
            # see if our dataset name was modified to avoid collisions
        
        # persist the data to RFiles in HDFS
        # rdd should consist of dicts
        
        # reserve an output dir in HDFS
        outputPath = client.getNewSparkJobOutputPath()
        importId = int(outputPath.split('/')[-1])
        
        conf = {'koverse.versionedCollectionId': coll.versionedCollectionId}
        
        # conf should contain the settings necessary for the
        # accumulo output format
        pairRdd = rdd.map(lambda r: (None, r))
        
        pairRdd.saveAsNewAPIHadoopFile(
            outputPath + '/files',
            'com.koverse.mapreduce.KoverseFileOutputFormat',
            keyClass = 'org.apache.hadoop.io.NullWritable',
            valueClass = 'java.util.Map',
            valueConverter = 'com.koverse.sdk.spark.converters.ToMapConverter',
            conf = conf)
        
        # tell koverse server to load files into data store
        client.addFilesToDataset(datasetName, outputPath)
        
        client.cleanupSparkImportDir(importId)


