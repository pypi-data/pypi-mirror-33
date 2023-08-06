import time
import os

class log:
    __logfile = False;
    __color = True;
    __withdate = False;

    __error = '\x1b[1;31m'
    __info = '\x1b[1;34m'
    __pass = '\x1b[1;32m'
    __warn = '\x1b[1;33m'
    __debug = '\x1b[1m'
    __default = '\x1b[0m'
    __path = os.getcwd()

    __levels = {"pass": __pass,
                "info": __info,
                "warn": __warn,
                "error": __error,
                "debug": __debug}

    def __init__(self):
        self.__debug =  False;
        self.__logfile = False;

    def setColor(self, color):
        self.__color = color

    def setPass(self, color):
        self.__pass = color
        self.__initColors("pass", self.__pass)

    def setInfo(self, color):
        self.__info = color
        self.__initColors("info", self.__info)

    def setError(self, color):
        self.__error = color
        self.__initColors("error", self.__error)

    def setWarn(self, color):
        self.__warn = color
        self.__initColors("warn", self.__warn)

    def setDebug(self, color):
        self.__debug = color
        self.__initColors("debug", self.__debug)

    def setLogfile(self, logfile):
        self.__logfile = logfile

    def setLogfileDate(self, date):
        self.__withdate = date

    def Info(self, msg):
        self.__output("info", msg)

    def Warn(self, msg):
        self.__output("warn", msg)

    def Error(self, msg):
        self.__output("error", msg)

    def Pass(self, msg):
        self.__output("pass", msg)

    def Debug(self, msg):
        self.__output("debug", msg)

    def __initColors(self, level, color):
        self.__levels[level] = color;

    def __output(self, level, msg):
        t = time.localtime()
        t_string = "{}-{}-{} {}:{}:{}".format(t.tm_year, str(t.tm_mon).zfill(2), str(t.tm_mday).zfill(2), str(t.tm_hour).zfill(2), str(t.tm_min).zfill(2), str(t.tm_sec).zfill(2))
        if self.__color == True:
            print('{}{}{}[{}] {}'.format(self.__levels[level], level.upper(), self.__default, t_string, msg))
        else:
            print('{}[{}] {}'.format(level.upper(), t_string, msg))

        if self.__logfile != False:
            t_filestring = "{}-{}-{}".format(t.tm_year, str(t.tm_mon).zfill(2), str(t.tm_mday).zfill(2))
            logfile = '{}/{}_{}.log'.format(self.__path, t_filestring, self.__logfile)
            with open(logfile, "a") as f:
                f.write('{}[{}] {}\n'.format(level.upper(), t_string, msg))