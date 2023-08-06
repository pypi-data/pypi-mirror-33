
from sklearn import metrics



outputPath = "../output"
datasetName= "/dataAugmentation"

auxPath = outputPath + datasetName
filePrediction = auxPath +"/predictionResults.csv"
predictions = []
csvfile = open(filePrediction, "r")
csvfile.readline()
for line in csvfile:
    line = line.split(",")
    predictions.append(int(line[1]))




groundTruthFile = "../test_GroundTruth.csv"
groundTruth = []
csvfile2 = open(groundTruthFile, "r")
csvfile2.readline()
for line in csvfile2:
    line = line.split(",")
    groundTruth.append(int(float(line[1])))

print("Ground Truth")
print (groundTruth)
print("Predictions")
print(predictions)

print(metrics.roc_auc_score(groundTruth, predictions))
print(metrics.accuracy_score(groundTruth,predictions))