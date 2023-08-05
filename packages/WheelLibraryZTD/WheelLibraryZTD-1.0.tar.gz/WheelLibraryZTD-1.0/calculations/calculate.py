from filemanager_.loadFile import *
from structurefile.station import Station
from structurefile.CSVFile import CSVFile

def calculateZTD():
    nameStation = input('Enter ID station: ')
    station = Station()
    station.setID(nameStation)
    folderName = input('Enter the folder name where are measurements: ')
    try:
        filenames = find_csv_files(folderName)
        for name in filenames:
            file = CSVFile()
            file.setName(name)
            file.setDate(datetime.strptime(file.getName()[8:19], '%Y%m%d_%H'))
            station.getListFiles().append(file)
            readCSVFiles(folderName + '//' + name, station)
        station.calcZTD_avarege()
    except FileNotFoundError:
        print("Don't find %s directory! " % folderName)
    return station
