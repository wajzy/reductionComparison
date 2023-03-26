import csv, random
from enum import Enum, auto
from sklearn.decomposition import PCA

class Type(Enum):
    INPUT = auto()
    INTERMEDIATE = auto()
    OUTPUT = auto()

class Reduction:
    def __init__(self, mtx, labels):
        self.mtx = mtx
        self.labels = labels

    @classmethod
    def loadFile(cls, fileName):
        mtx = {}
        with open(fileName, 'r') as f:
            csvReader = csv.reader(f, delimiter=';', quotechar='"')
            titles = next(csvReader)[1:-1]
            labels = {label : set() for label in titles}
            for row in csvReader:
                mtx[row[0]] = {titles[idx] : float(weight.replace(',', '.')) for idx, weight in enumerate(row[1:-1])}
                type = Type.INTERMEDIATE
                if row[-1].upper() == 'I':
                    type = Type.INPUT
                elif row[-1].upper() == 'O':
                    type = Type.OUTPUT
                labels[row[0]].add(type)
        return cls(mtx, labels)

    def isInputConcept(self, concept):
        return Type.INPUT in self.labels[concept]

    def isOutputConcept(self, concept):
        return Type.OUTPUT in self.labels[concept]

    def isIntermediateConcept(self, concept):
        return Type.INTERMEDIATE in self.labels[concept]

    def getRowAsList(self, label):
        return list(self.mtx[label].values())

    def getColumnAsList(self, label):
        col = []
        for row in self.mtx.values():
            col.append(row[label])
        return col

    def createWideMatrix(self):
        '''It creates a matrix, each row of which contains the weights of edges starting from and leading to a certain intermediate concept.

        Returns
        -------
        list
            A wide matrix to be clustered.
        '''
        wideMtx = []
        for label in self.labels:
            if self.isIntermediateConcept(label):
                row = []
                row.extend(self.getRowAsList(label))
                row.extend(self.getColumnAsList(label))
                wideMtx.append(row)
        return wideMtx

    def addNoiseToMatrix(self, matrix):
        '''Adds further rows to the matrix until the number of rows is less then the number of columns. 

        Parameters
        ----------
        matrix : list

        Returns
        -------
        list
            An extended matrix created by adding Gauss-noise to copies of existing rows.
        '''
        newMtx = [row[:] for row in matrix]
        while len(newMtx) < len(matrix[0]):
            for r in range(len(matrix)):
                newRow = []
                for c in range(len(matrix[r])):
                    newRow.append(max(-1., min(1., matrix[r][c] + random.gauss(0, 0.005))))
                newMtx.append(newRow)
        return newMtx

    def reduceDimensions(self, wideMatrix, dimensions):
        return PCA(n_components=dimensions).fit_transform(self.addNoiseToMatrix(wideMatrix))

    def calcWeight(self, clusters, clusterFrom, clusterTo):
        '''Calculates the weight of connection between two clusters

        Parameters
        ----------
        clusters : dict
            The key is the cluster's label, the value is a set containing the concepts.
        clusterFrom : string
            Label of the source cluster.
        clusterTo : string
            Label of the destination cluster.

        Returns
        -------
        float
            The weight of connection between clusterFrom and clusterTo.
        '''
        sumWeigth = 0.
        connections = 0
        for conceptFrom in clusters[clusterFrom]:
            for conceptTo in clusters[clusterTo]:
                sumWeigth += self.mtx[conceptFrom][conceptTo]
                connections += 1
        if connections == 0:
            return 0
        else:
            return sumWeigth / connections

    def calcAllWeights(self, clusters):
        '''Calculates the weight matrix of the reduced model

        Parameters
        ----------
        clusters : dict
            Clusters of the reduced model.
        
        Returns
        -------
        dict
            The weight matrix of the reduced model.
        '''
        mtx = {}
        for clusterFrom in clusters:
            row = {}
            for clusterTo in clusters:
                row[clusterTo] = self.calcWeight(clusters, clusterFrom, clusterTo)
            mtx[clusterFrom] = row
        return mtx
