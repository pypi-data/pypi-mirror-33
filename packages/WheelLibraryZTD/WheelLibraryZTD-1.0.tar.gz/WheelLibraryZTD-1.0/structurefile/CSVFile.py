from datetime import *


class CSVFile:
    __name = ""
    __listRecords = []
    __date = datetime

    def __init__(self):
        self.__listRecords = []
        self.__name = ''
        self.__date = datetime

    def addRecord(self, record):
        self.__listRecords.append(record)

    # Settery

    def setName(self, name):
        self.__name = name

    def setDate(self, date):
        self.__date = date

    # Gettery

    def getName(self):
        return self.__name

    def getDate(self):
        return self.__date

    def getListRecords(self):
        return self.__listRecords
