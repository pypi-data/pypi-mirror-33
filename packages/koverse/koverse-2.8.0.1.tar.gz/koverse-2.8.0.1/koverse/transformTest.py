from pyspark import SparkContext
import sys
sys.path.append('../')
from koverse import client

class PySparkTransformTestRunner(object):
    '''This class can be used to test new PySparkTransforms by running them on local or remote data'''
    
    def __init__(self, params, transformClass):
        self.params = params
        self.transformClass = transformClass
    
    def testOnLocalData(self, inputDatasets):
        
        sc = SparkContext('local', 'PySparkTransformTestRunner')
        
        # create a set of RDDs for the input records
        rdds = {}
        i = 0
        for inputDataset in inputDatasets:
            rdd = sc.parallelize(inputDataset)
            rdds[str(i)] = rdd
            
        return self._runTest(rdds, sc)
    
    def testOnRemoteData(self, remoteDatasets, hostname, username, password, sc):
        client.connect(hostname)
        client.authenticateUser(username, password)
        
        rdds = {}
        for remoteDataset in remoteDatasets:
            conf = client.getSparkRDDConf(remoteDataset)
            rdd = sc.newAPIHadoopRDD(
                'com.koverse.mapreduce.KoverseInputFormat',
                'org.apache.hadoop.io.Text',
                'java.util.HashMap',
                conf = conf)
            rdds[remoteDataset] = rdd.map(lambda r: r[1])
        
        return self._runTest(rdds, sc)
    
    # internal
    def _runTest(self, rdds, sc):
        
        transform = self.transformClass(self.params)
        
        return transform.execute(rdds, sc).collect()
        
