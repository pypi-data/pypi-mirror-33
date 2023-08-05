class Station:
    __stationID = ''
    __listFiles = []
    __dict = {}

    def __init__(self):
        self.__dict = {}
        self.__listFiles = []
        self.__stationID = ''

    def calcZTD_avarege(self):
        numberFile = 0
        for file in self.__listFiles:
            for record in file.getListRecords():
                if self.__dict[record.getDate()] == '':
                    depth = 0
                    dict_rec_depth = {}
                    dict_rec_depth[0] = record.getZTD()
                    self.checkFiles(depth + 1, record.getDate(), numberFile + 1, dict_rec_depth)
                    counter = 0
                    sumWeight = 0
                    for i in dict_rec_depth:
                        counter = counter + (dict_rec_depth[i]*(1/(2+(len(dict_rec_depth)-i-1))))
                        sumWeight = sumWeight + (1/(2+(len(dict_rec_depth)-i-1)))
                    averageZTD = counter/sumWeight
                    self.__dict[record.getDate()] = averageZTD
            numberFile = numberFile + 1

    def checkFiles(self, depth, date, numberFile, dict_rec_depth):
        for file in self.__listFiles[numberFile:len(self.__listFiles)]:
            for record in file.getListRecords():
                if record.getDate() > date:
                    break
                if record.getDate() == date:
                    dict_rec_depth[depth] = record.getZTD()
                    depth = depth + 1

    def getDict(self):
        return self.__dict

    def getListFiles(self):
        return self.__listFiles

    def setID(self, stationID):
        self.__stationID = stationID

    def getID(self):
        return self.__stationID
