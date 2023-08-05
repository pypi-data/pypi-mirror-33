import csv
from datetime import *
from structurefile.record import Record
from os import listdir

def find_csv_files(folderName):
    suffix = ".csv"
    filenames = listdir(folderName)
    return [filename for filename in filenames if filename.endswith(suffix)]

def loadDataFromCSV(reader, station, stationID):
    for row in reader:
        if row[2] == stationID.upper():
            record = Record()
            record.setDate(datetime.strptime(row[0] + ' ' + row[1], "%Y-%m-%d %H:%M"))
            station.getDict()[record.getDate()] = ''
            record.setID(row[2])
            record.set2m_interp(row[3])
            record.setLat(float(row[4]))
            record.setLon(float(row[5]))
            record.setCoordinate_X(int(row[6]))
            record.setCoordinate_Y(int(row[7]))
            record.setHeightStation(float(row[8]))
            record.setHeightWRF(float(row[9]))
            record.setTemp(float(row[10]))
            record.setHumidity(float(row[11]))
            record.setPressure(float(row[12]))
            record.interpolation()
            record.setZTD(record.calcZTD())
            station.getListFiles()[len(station.getListFiles())-1].addRecord(record)


def readCSVFiles(filePath, station):
    try:
        with open(filePath, 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            loadDataFromCSV(reader, station, station.getID())
    except FileNotFoundError:
            print("Error with opening file! ")
