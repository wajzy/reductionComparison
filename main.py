from ftr import FTR
from km import KM

from reduction import Reduction

original = FTR.loadFile('simpleTest.csv')
print(original.mtx)
print(original.labels)
FTRreduced = original.getReducedModel(0.18)
print(FTRreduced.mtx)
print(FTRreduced.labels)

KMreduced = KM(original.mtx, original.labels).getReducedModel(5, 10)
print(KMreduced.mtx)
print(KMreduced.labels)
