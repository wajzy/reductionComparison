import reduction, math

class FTR(reduction.Reduction):
    def __init__(self, mtx, labels):
        super().__init__(mtx, labels)

    def distance(self, fromConcept, toConcept, maxDistance, cluster):
        ''' Calculating the distance of concepts

        Parameters
        ----------
        fromConcept : string
            Label of the 1st concept.
        toConcept : string
            Label of the 2nd concept.
        maxDistance : float
            If the distance of the concepts are greater than this value, they are considered to far to be merged.
        cluster : set
            The concepts of the current cluster merged so far.

        Returns
        -------
        bool
            True if the distance of fromConcept and toConcept is less than or equal to mxDistance, False otherwise.
        '''
        sumWeigth = 0.
        edgePairs = 0
        for concept in self.labels:
            if concept!=fromConcept and concept!=toConcept and concept not in cluster:
                # outgoing edges
                w1 = self.mtx[fromConcept][concept]
                w2 = self.mtx[toConcept][concept]
                sumWeigth += (w1-w2)**2
                # incoming edges
                w1 = self.mtx[concept][fromConcept]
                w2 = self.mtx[concept][toConcept]
                sumWeigth += (w1-w2)**2
                edgePairs += 1
        sumWeigth /= edgePairs*8
        return math.sqrt(sumWeigth) <= maxDistance

    def buildCluster(self, initConcept, maxDistance):
        '''Builds a new cluster

        Parameters
        ----------
        initConcept : string
            The initial concept of the new cluster.
        maxDistance : float
            The maximum distance allowed between the candidate concept and current elements of the cluster to be included in the cluster.

        Returns
        -------
        set
            The new cluster.
        '''
        cluster = {initConcept}
        for concept in self.labels:
            if concept!=initConcept and not self.isInputConcept(concept) and not self.isOutputConcept(concept):
                elementOfCluster = True
                for member in cluster:
                    elementOfCluster = self.distance(member, concept, maxDistance, cluster)
                    if elementOfCluster == False:
                        break
                if elementOfCluster:
                    cluster.add(concept)
        return cluster

    def isUniqueCluster(self, existingClusters, newCluster):
        '''Determines whether newCluster is included in existingClusters or not

        Parameters
        ----------
        existingClusters : dict
            Dict of clusters.
        newSet : set
            A cluster.

        Returns
        -------
        bool
            True if an equivalent cluster of newCluster is already included in existingClusters, False otherwise.
        '''
        for label in existingClusters:
            if existingClusters[label] == newCluster:
                return False
        return True

    def buildAllClusters(self, maxDistance):
        '''Starts the cluster building process

        Parameters
        ----------
        maxDistance : float
            Design parameter in the interval [0, 1] to define the extent of merger.

        Returns
        -------
        dict
            The dictionary of clusters.
        '''
        clusters = {}
        index = 1
        for concept in self.labels:
            if self.isInputConcept(concept) or self.isOutputConcept(concept):
                clusters['K'+str(index)] = {concept}
                index += 1
            else:
                cluster = self.buildCluster(concept, maxDistance)
                if self.isUniqueCluster(clusters, cluster):
                    clusters['K'+str(index)] = cluster
                    index += 1
        return clusters

    def calcLabels(self, clusters):
        '''Defines the labels of the reduced model

        Parameters
        ----------
        clusters : dict
            Clusters of the reduced model.

        Returns
        -------
        dict
            The labels of the reduced model.
        '''
        labels = {}
        for cluster in clusters:
            if len(clusters[cluster])==1:
                concept = next(iter(clusters[cluster]))
                if self.isInputConcept(concept):
                    labels[cluster] = {reduction.Type.INPUT}
                elif self.isOutputConcept(concept):
                    labels[cluster] = {reduction.Type.OUTPUT}
            else:
                labels[cluster] = {reduction.Type.INTERMEDIATE}
        return labels

    def getReducedModel(self, maxDistance):
        '''Creates a reduced model based on the current one.

        Parameters
        ----------
        maxDistance : float
            Design parameter in the interval [0, 1] to define the extent of merger.

        Returns
        -------
        FTR
            A new, reduced model.
        '''
        clusters = self.buildAllClusters(maxDistance)
        return FTR(self.calcAllWeights(clusters), self.calcLabels(clusters))
