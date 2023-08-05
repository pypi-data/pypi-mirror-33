from datetime import *
import math

class Record:
    __dateTime = datetime
    __stationID = ''
    __2m_interp = ''
    __lat = 0
    __lon = 0
    __coordinate_X = 0
    __coordinate_Y = 0
    __temp = 0
    __heightStation = 0
    __heightWRF = 0
    __humidity = 0
    __pressure = 0
    __hour = 0
    __ZTD = 0
    __gamma = 0.0065
    __M = 0.0289644
    __R = 8.31432

    def __init__(self):
        self.__dateTime = datetime
        self.__2m_interp = ''
        self.__lat = 0
        self.__lon = 0
        self.__coordinate_X = 0
        self.__coordinate_Y = 0
        self.__temp = 0
        self.__heightStation = 0
        self.__heightWRF = 0
        self.__humidity = 0
        self.__pressure = 0
        self._ZTD = 0

    def toString(self):
        return str(self.__date) + ' ' + self.__stationID + ' ' + self.__2m_interp + ' ' +\
               str(self.__lat) + ' ' + str(self.__lon) + ' ' + str(self.__coordinate_X) +\
               ' ' + str(self.__coordinate_Y) + ' ' + str(self.__heightStation) + ' ' +\
               str(self.__heightWRF) + ' ' + str(self.__temp) + ' ' + str(self.__humidity) +\
               ' ' + str(self.__pressure)

    def interpolation(self):
        if self.__2m_interp == "2m":
            self.__pressure = self.__pressure * ((self.__temp - self.__gamma
                                                  * (self.__heightStation - self.__heightWRF))/self.__temp) **\
                              (self.calc_g() * self.__M / self.__R * self.__gamma)

    def calc_g(self):
        return 9.8063*(1-(10**-7)*((self.__heightWRF + self.__heightStation)/2.0)
                       * (1-0.0026373*math.cos(2*self.__lat) + 5.9*(10**-6)*math.cos(2*self.__lat)**2))

    def calc_e(self):
        return (self.__humidity * self.calc_e_sat())/100

    def calc_e_sat(self):
        return 6.112 * math.e ** ((17.67 * (self.__temp - 273.15))/((self.__temp-273.15) + 243.5))

    def calcZTD(self):
        return 0.002277*(self.__pressure + ((1255/self.__temp)+0.05)*self.calc_e())

    # Settery

    def setDate(self, date):
        self.__dateTime = date

    def setHeightStation(self, height):
        self.__heightStation = height

    def setHeightWRF(self, height):
        self.__heightWRF = height

    def setZTD(self, ztd):
        self.__ZTD = ztd

    def setID(self, stationID):
        self.__stationID = stationID

    def set2m_interp(self, interp):
        self.__2m_interp = interp

    def setLat(self, lat):
        self.__lat = lat

    def setLon(self, lon):
        self.__lon = lon

    def setCoordinate_X(self, coordinate_X):
        self.__coordinate_X = coordinate_X

    def setCoordinate_Y(self, coordinate_Y):
        self.__coordinate_Y = coordinate_Y

    def setTemp(self, Temp):
        self.__temp = Temp

    def setHumidity(self, humidity):
        self.__humidity = humidity

    def setPressure(self, pressure):
        self.__pressure = pressure

    # Gettery

    def getDate(self):
        return str(self.__dateTime)

    def getZTD(self):
        return self.__ZTD

    def getID(self):
        return self.__stationID

    def get2m_interp(self):
        return self.__2m_interp

    def getLat(self):
        return self.__lat

    def getLon(self):
        return self.__lon

    def getToordinate_X(self):
        return self.__coordinate_X

    def getToordinate_Y(self):
        return self.__coordinate_Y

    def getTemp(self):
        return self.__temp

    def getHumidity(self):
        return self.__humidity

    def getPressure(self):
        return self.__pressure
