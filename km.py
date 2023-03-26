import reduction
from sklearn.cluster import KMeans

class KM(reduction.Reduction):
    def __init__(self, mtx, labels):
        super().__init__(mtx, labels)

    def buildAllClusters(self, numClusters, dimensions):
        wideMatrix = self.createWideMatrix()
        numIntermediates = len(wideMatrix)
        kmeans = KMeans(n_clusters=numClusters).fit(self.reduceDimensions(wideMatrix, dimensions))
        clusters = {}
        labels = {}
        k = 1
        for concept in self.labels:
            if self.isInputConcept(concept):
                cluster = 'K'+str(k) 
                clusters[cluster] = {concept}
                labels[cluster] = {reduction.Type.INPUT}
                k += 1
        m = 0
        firstIntermediate = k
        for concept in self.labels:
            if self.isIntermediateConcept(concept):
                cluster = 'K'+str(firstIntermediate + kmeans.labels_[m])
                if cluster in clusters:
                    clusters[cluster].add(concept)
                else:
                    clusters[cluster] = {concept}
                    labels[cluster] = {reduction.Type.INTERMEDIATE}
                    k += 1
                m += 1
        for concept in self.labels:
            if self.isOutputConcept(concept):
                cluster = 'K'+str(k) 
                clusters[cluster] = {concept}
                labels[cluster] = {reduction.Type.OUTPUT}
                k += 1
        return (clusters, labels)
    
    def getReducedModel(self, numClusters, dimensions):
        clusters, labels = self.buildAllClusters(numClusters, dimensions)
        return KM(self.calcAllWeights(clusters), labels)
        
        