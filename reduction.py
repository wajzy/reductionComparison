import csv
from enum import Enum, auto

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

            