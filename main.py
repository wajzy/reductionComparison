from ftr import FTR

original = FTR.loadFile('simpleTest.csv')
print(original.mtx)
print(original.labels)
reduced = original.getReducedModel(0.18)
print(reduced.mtx)
print(reduced.labels)
