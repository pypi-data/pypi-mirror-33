import csv

def saveDataToFile(station, stationID):
    w = csv.writer(open(stationID + '.csv', 'w', newline=''))
    for key, val in station.getDict().items():
        w.writerow([key, val])
        print([key, val])
