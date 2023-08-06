import logging
import inspect
import os
import sys
import traceback
import random
import json
import time
import stat
import shutil
from os import path, pathsep
from fnmatch import fnmatch
from ast import literal_eval
from shutil import rmtree
from logging.handlers import TimedRotatingFileHandler


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class JsonConfig:

    def __init__(self, configFile: str):
        self.ConfigFile = configFile
        self.__loadFile()

    def __loadFile(self):
        file = open(self.ConfigFile, 'r')
        self.Map = json.load(file)

    def getKey(self, keyName: str):
        return self.Map[keyName]

    def setKey(self, keyName: str, value) -> None:
        self.Map[keyName] = value

    def writeConfig(self):
        file = open(self.ConfigFile, 'w+')
        json.dump(self.Map, file)
        file.close()


class App(metaclass=Singleton):

    def __init__(self):
        self.__AppContext = {'MODULES': {}}
        self.AppBase = self.getAppBase()
        self.AppName = self.getAppName()
        self.AppSettings = None
        self.__initProjectDirs()
        self.__populateAppSettings()
        self.__initLogger()

    def __populateAppSettings(self):
        appSettingsModule = __import__(self.AppName+'.conf.'+self.AppName+'_properties', fromlist=[''])
        self.AppSettings = appSettingsModule.AppSettings()

    def __initLogger(self):
        filename = self.getProjectBase()+'/logs/'+self.AppName+'.log'
        self.logger = AppLogger(appName=self.AppName).getLogger(logFilename=filename,
                                                                appSettings=self.AppSettings)

    def __initProjectDirs(self):
        fps = os.path.sep
        projectBase = self.getProjectBase()
        projectDirs = [projectBase+fps+'conf', projectBase+fps+'logs', projectBase+fps+'data', projectBase+fps+'tmp']
        for d in projectDirs:
            if not FileUtils().dirExists(d):
                FileUtils().createDir(d)

    def injectModule(self):
        modCaller = Inspector.getCallerMod()
        modName = modCaller.split('_')[0]
        try:
            return App().__AppContext['MODULES'][modName]
        except KeyError:
            fps = os.path.sep
            confDir = self.AppBase+fps+'conf'
            modCfgFile = confDir+fps+modName+'.ini'
            manCfgFile = confDir+fps+modName+'_manifest.ini'
            verConfigManager = ConfigManager(configFile=manCfgFile)
            modVersion = literal_eval(verConfigManager.getValue(sectionName='MODULE_INFO',
                                                                propertyName='Version'))
            modConfigManager = ConfigManager(configFile=modCfgFile)
            modSettings = modConfigManager.getConfigMap()
            appModule = AppModule(name=modName, version=modVersion, settings=modSettings)
            App().__AppContext['MODULES'][modName] = appModule
            return appModule

    def getAppModule(self, moduleName):
        return self.__AppContext['MODULES'][moduleName]

    @staticmethod
    def getMyAppModule():
        modCaller = Inspector.getCallerMod()
        modName = modCaller.split('_')[0]
        try:
            return App().__AppContext['MODULES'][modName]
        except KeyError:
            raise FrameworkException(errorMessage='Module by name ['+modName+'] has not yet been injected into app context')


    @staticmethod
    def getAppBase():
        basePath = FileUtils.getParentDir(FileUtils.getParentDir(__file__))
        return basePath

    @staticmethod
    def getProjectBase():
        basePath = FileUtils.getParentDir(FileUtils.getParentDir(FileUtils.getParentDir(__file__)))
        return basePath

    def getAppName(self):
        iniFile = self.getProjectBase()+'/project_manifest.ini'
        iniConfig = ConfigManager(configFile=iniFile)
        appName = iniConfig.getValue('APP', 'AppName')
        return appName.lower()

    def getAppVersion(self):
        iniFile = self.getProjectBase()+'/project_manifest.ini'
        iniConfig = ConfigManager(configFile=iniFile)
        appVersion = iniConfig.getValue('APP', 'AppVersion')
        return appVersion

    def getAppLogFilename(self):
        logDir = self.getProjectBase() + PlatformProperty.FileSep + 'logs'
        return logDir + PlatformProperty.FileSep + self.AppName + '.log'

    def logd(self, msg):
        self.logger.debug(msg)

    def logi(self, msg):
        self.logger.info(msg)

    def logw(self, msg):
        self.logger.warn(msg)

    def loge(self, msg):
        self.logger.error(msg)

    def logc(self, msg):
        self.logger.critial(msg)

    def addAppContext(self, keyName, keyValue):
        reservedKeys = ['MODULES']
        if keyName in reservedKeys:
            raise FrameworkException('The keyName specified is a reserved key in the app context, choose another name')
        try:
            self.__AppContext[keyName]
            raise FrameworkException('The keyName has already been registered. Use the updateAppContext method to change value')
        except KeyError:
            self.__AppContext[keyName] = keyValue


class AppModule(metaclass=Singleton):

    __package__ = 'applibs'

    def __init__(self, name, version, settings):
        self.Name = name
        self.Version = str(version['MAJOR'])+str(version['MINOR'])
        self.ModuleSettings = settings
        self.Context = {}
        self.logger = AppLogger(App().AppName).getModuleLogger(modName=self.Name,
                                                               logFilename=self.getLogFilename(),
                                                               modSettings=self.ModuleSettings)

    def getLogFilename(self):
        fsp = PlatformProperty.FileSep
        return App().getProjectBase()+fsp+'logs'+fsp+self.Name+'.log'

    def logd(self, msg):
        self.logger.debug(msg)

    def logi(self, msg):
        self.logger.info(msg)

    def logw(self, msg):
        self.logger.warn(msg)

    def loge(self, msg):
        self.logger.error(msg)

    def logc(self, msg):
        self.logger.critial(msg)


class AppLogger(metaclass=Singleton):

    def __init__(self, appName: str=None):
        self.AppName = appName if appName is not None else 'app'
        self.RootLogger = logging.getLogger(appName)
        self.RootLogger.setLevel(logging.DEBUG)
        self.logger = self.RootLogger
        self.CONSOLE_LOG_LEVEL_NUM = 45
        logging.addLevelName(self.CONSOLE_LOG_LEVEL_NUM, "CONSOLE")
        logging.Logger.console = self.__doConsoleLog

    def __doConsoleLog(self, message, *args, **kwargs):
        if self.logger.isEnabledFor(self.CONSOLE_LOG_LEVEL_NUM):
            self.logger._log(self.CONSOLE_LOG_LEVEL_NUM, message, args, **kwargs)

    @staticmethod
    def __getLogDir(logfile):
        lfArray = logfile.split(os.path.sep)
        logDir = logfile[:-(len(lfArray[len(lfArray)-1]))]
        return logDir

    def __getFileHandler(self, logfile: str, retention: int = 7, level: str = 'INFO'):
        logDir = self.__getLogDir(logfile)
        if not FileUtils.dirExists(logDir):
            FileUtils.createDir(logDir)
        fileHandler = TimedRotatingFileHandler(filename=logfile,
                                               when='D',
                                               interval=1,
                                               backupCount=retention)
        fileFormat = logging.Formatter('%(levelname)-6s|%(name)-10s|%(threadName)-10s|%(lineno)-3d|%(asctime)s.%(msecs)-3d|:: %(message)s',
                                       '%m.%d.%y %H:%M:%S')
        fileHandler.setLevel(logging.getLevelName(level))
        fileHandler.setFormatter(fileFormat)
        return fileHandler

    @staticmethod
    def __getConsoleHandler():
        consoleHandler = logging.StreamHandler()
        consoleFormat = logging.Formatter('::| %(message)s')
        consoleHandler.setLevel(logging.getLevelName('CONSOLE'))
        consoleHandler.setFormatter(consoleFormat)
        return consoleHandler

    def getLogger(self, logFilename, appSettings):
        logger = logging.getLogger(self.AppName)
        logger.addHandler(self.__getFileHandler(logfile=logFilename,
                                                retention=appSettings['LOGGING']['FileRetention'],
                                                level=appSettings['LOGGING']['FileLevel']))
        logger.addHandler(self.__getConsoleHandler())
        return logger

    def getAppClassLogger(self, className, appSettings):
        pyModule = Inspector().getCallerMod()
        loggerName = self.AppName.lower()+'.'+pyModule+'.'+className
        try:
            level = appSettings['LOGGING']['ClassLoggers'][loggerName]['Level']
            logger = logging.getLogger(loggerName)
            logger.setLevel(level)
            return logger
        except KeyError:
            return logging.getLogger(loggerName)

    def getModuleLogger(self, modName, logFilename, modSettings):
        modName = Inspector().getCallerAppModName()
        loggerName = self.AppName.lower()+'.'+modName
        modLogger = logging.getLogger(loggerName)
        modLogger.addHandler(self.__getFileHandler(logfile=logFilename,
                                                   retention=modSettings['LOGGING']['FileRetention'],
                                                   level=modSettings['LOGGING']['FileLevel']))
        return modLogger

    def getModuleClassLogger(self, modName, className, modSettings):
        pyModule = Inspector().getCallerMod()
        loggerName = self.AppName.lower()+'.'+modName+'.'+pyModule+'.'+className
        try:
            level = modSettings['LOGGING']['ChildLoggers'][loggerName]['Level']
            logger = logging.getLogger(loggerName)
            logger.setLevel(level)
            return logger
        except KeyError:
            return logging.getLogger(loggerName)

    def getAppLibLogger(self, className):
        pyModule = Inspector().getCallerMod()
        loggerName = self.AppName.lower()+'.pylegos.'+pyModule+'.'+className
        return logging.getLogger(loggerName)


class FileUtils(object):

    @staticmethod
    def getParentDir(filePath):
        return os.path.dirname(os.path.abspath(filePath))

    def getAppBase(self):
        callingFile = Inspector.getCallerFilePath()
        return self.getParentDir(filePath=callingFile)

    def getModuleAppBase(self):
        callingFile = Inspector.getCallerFilePath()
        basePath = os.path.dirname(os.path.dirname(self.getParentDir(filePath=callingFile)))
        return basePath

    def getAppProjectBase(self):
        callingFile = Inspector.getCallerFilePath()
        basePath = os.path.dirname(self.getParentDir(filePath=callingFile))
        return basePath

    def getModuleProjectBase(self):
        callingFile = Inspector.getCallerFilePath()
        basePath = os.path.dirname(os.path.dirname(os.path.dirname(self.getParentDir(filePath=callingFile))))
        return basePath

    @staticmethod
    def getWorkingDir():
        return os.getcwd()

    @staticmethod
    def changeWorkingDir(newDir):
        os.chdir(newDir)

    @staticmethod
    def dirExists(directoryPath):
        '''
        Use to check if a directory exists.  This will only return true
        if it exists and is also a directory (as opposed to a file)
        :param directoryPath: The full path to the directory
        :return: Boolean (True|False)
        '''
        return os.path.isdir(directoryPath)

    @staticmethod
    def fileExists(filePath):
        '''
        Used to check if file exists.  It will return true if the file
        exists and it is a file, not a directory
        :param filePath: Full path to the file
        :return: Boolean (True|False)
        '''
        return os.path.isfile(filePath)

    def fileMatchExist(self, baseDir, pattern, strictCheck=True):
        """
        Use to check if a file exists based on a pattern. The pattern that is used is
        simple unix style wildcard. (i.e. conf* will batch config, configs, configuration).
        It will only return True if the file is a file, not a directory.  If do not care if
        it is a file or directory, set optional parameter useStrictCheck to False
        :param baseDir: The directory to look in
        :param pattern: The pattern to use for match
        :param strictCheck: Indicates if it should make sure the match is a file Default is True
        :return: Boolean
        """
        matchExists = False
        fileMatches = []
        for file in os.listdir(baseDir):
            if fnmatch(file, pattern):
                fileMatches.append(file)

        if strictCheck:
            for match in fileMatches:
                if self.fileExists(filePath=baseDir+PlatformUtils.FileSep+match):
                    matchExists = True
                    break
        else:
            if len(fileMatches > 0):
                matchExists = True

        return matchExists

    def dirMatchExist(self, baseDir, pattern, strictCheck=True):
        '''
        Used to check to see if a directory that matches a pattern exists.  The pattern is
        a unix style directory match pattern. (i.e. Conf* will match Conf,Config,Configuration,etc)
        It will only return true if the object that matches is a directory, not a file.  If you
        do not care if match is a directory, but also want to return if a file is found that matches
        the pattern, set the optional parameter strict check to False.
        :param baseDir:  The base directory to look in
        :param pattern: The unix style pattern to check
        :param strictCheck: Indicates if only a directory will be considered a match. Default is True
        :return: Boolean
        '''
        matchFound = False
        matchedDirs = []
        for directory in os.listdir(baseDir):
            if fnmatch(directory, pattern):
                matchedDirs.append(directory)

        if strictCheck:
            for match in matchedDirs:
                if self.dirExists(directoryPath=baseDir+PlatformUtils.FileSep+match):
                    matchFound = True
                    break
        else:
            if len(matchedDirs > 0):
                matchFound = True

        return matchFound

    def getFileMatches(self, baseDir, pattern, strictCheck=True):
        """
        This will return true if a list of files that match the pattern.  If there are
        no matching files, then an empty list is returned
        :param baseDir: The directory to search in.
        :param pattern: Pattern to search for (ie conf*)
        :param strictCheck: Indicates to only include file objects (not directories) that match
        :return: List<String>
        """
        matches = []
        fileMatches = []
        for file in os.listdir(baseDir):
            if fnmatch(file, pattern):
                matches.append(file)
        if strictCheck:
            for match in matches:
                if self.fileExists(filePath=baseDir+PlatformUtils.FileSep+match):
                    fileMatches.append(match)
        else:
            fileMatches = matches

        return fileMatches

    def getDirMatches(self, baseDir, pattern, strictCheck=True):
        """
        This will return true if a list of directories that match the pattern.  If there are
        no matching directories, then an empty list is returned
        :param baseDir: The directory to search in.
        :param pattern: Pattern to search for (ie conf*)
        :param strictCheck: Indicates to only include directory objects (not files) that match
        :return: List<String>
        """
        matches = []
        dirsFound = []
        for dir in os.listdir(baseDir):
            if fnmatch(dir, pattern):
                matches.append(dir)
        if strictCheck:
            for match in matches:
                if self.dirExists(directoryPath=baseDir+PlatformUtils.FileSep+match):
                    dirsFound.append(match)
        else:
            dirsFound = matches

        return dirsFound

    @staticmethod
    def createDir(dirPath):
        """
        Simple wrapper to os.makedirs.  Using this method so you can pass a full directory structure instead of
        creating the directories recursively.

        `dirPath:` Full path of directory to create
        `return:` None
        """
        os.makedirs(name=dirPath, exist_ok=True)

    @staticmethod
    def removeDir(dirPath, safeRemove=True):
        try:
            os.rmdir(dirPath)
        except OSError:
            if not safeRemove:
                rmtree(dirPath)

    def rmDirMatch(self, dirPath, pattern):
        dirMatches = []
        for d in os.listdir(dirPath):
            if fnmatch(d, pattern):
                dirMatches.append(d)

        for match in dirMatches:
            self.removeDir(dirPath=dirPath + PlatformUtils.FileSep + match)

    @staticmethod
    def getDirList(dirPath, matchFilesOnly=False, matchDirsOnly=False):
        """Simple method for listing directory contents.  Is not recursive, just lists
        contents directly under the dirPath argument
        """
        fsep = PlatformUtils.FileSep
        objects = []
        allObjects = os.listdir(dirPath)
        for file in allObjects:
            if matchFilesOnly:
                if os.path.isfile(dirPath+fsep+file):
                    objects.append(file)
            elif matchDirsOnly:
                if os.path.isdir(dirPath+fsep+file):
                    objects.append(file)
            else:
                objects.append(file)
        return objects

    @staticmethod
    def getFileModifiedAge(filename):
        ageInSeconds = int((time.time() - os.stat(filename)[stat.ST_MTIME]))
        return ageInSeconds

    @staticmethod
    def copyFile(sourceFile, targetFile):
        shutil.copy2(sourceFile, targetFile)

    @staticmethod
    def touchFile(filename):
        open(filename, 'a').close()


class JsonObject:

    class ObjectType:
        JSON = 'JSON'
        DICT = 'DICT'

    def serialize(self, objectType=ObjectType.DICT):
        if objectType == self.ObjectType.JSON:
            return json.dumps(self.__dict__, cls=JsonObjectEncoder, sort_keys=True)
        elif objectType == self.ObjectType.DICT:
            dictObject = {}
            for key, val in self.__dict__.items():
                dictObject[key] = self.__getDictValue(val)
            return dictObject
        else:
            raise RuntimeError('Invalid serialization method supplied to serialize()')

    def deserialize(self, data):
        if type(data) is str:
            self.__dict__ = json.loads(data)
        elif type(data) is dict:
            self.__dict__ = data

    @staticmethod
    def __getDictValue(val):
        if issubclass(type(val), JsonObject):
            return val.serialize()
        else:
            return val


class JsonObjectEncoder(json.JSONEncoder):

    def default(self, o):
        if hasattr(o, 'serialize'):
            return o.serialize()
        else:
            return json.JSONEncoder.default(self, o)


#


class Inspector(object):

    @staticmethod
    def getCallerFilePath(callLevel=2):
        return inspect.stack()[callLevel][1]

    @staticmethod
    def getCallerMod(callLevel=2):
        fileName = inspect.stack()[callLevel][1]
        modName = inspect.getmodulename(fileName)
        return modName

    @staticmethod
    def getCallerAppModName(callLevel=2):
        fileName = inspect.stack()[callLevel][1]
        modName = inspect.getmodulename(fileName)
        appModName = modName.split('_')[0]
        return appModName

    @staticmethod
    def getCallerFunc(callLevel=2):
        func = str(inspect.stack()[callLevel][3]).strip("'")
        return func

    @staticmethod
    def getCallerName(callLevel=2):
        sof = inspect.getouterframes(inspect.currentframe())[1][0]
        try:
            callerName = str(sof.f_locals['self']).split('.')[1].split()[0]
        except KeyError:
            try:
                callerName = sof.f_locals['__name__']
            except KeyError:
                cs = inspect.stack()
                callerName = cs[callLevel][3]

        return callerName

    @staticmethod
    def getCallerModAndClassName(callLevel=2):
        """ Function to get module.class of caller.  If caller does not come from a class, just
        the module name will be returned
        :return: The name of the caller in format module_name.ClassName
        """
        of = inspect.getouterframes(inspect.currentframe())[callLevel][0]
        try:
            callObj = of.f_locals['self']
            if isinstance(callObj, object):
                try:
                    packageName = inspect.getattr_static(callObj, '__package__')
                except AttributeError:
                    packageName = None
                moduleName = inspect.getattr_static(callObj, '__module__')
                className = str(of.f_locals['self']).split('<')[1].split()[0].split()[0].split('.')[1]
                if packageName is not None:
                    caller = packageName+'.'+moduleName+'.'+className
                else:
                    caller = moduleName+'.'+className
            else:
                raise KeyError()
        except IndexError:
            caller = of.f_locals['self']
        except KeyError:
            cs = inspect.stack()
            callObj = cs[callLevel+1][4][0].split('=')[1].strip()
            modName = inspect.getmodulename(cs[callLevel][1])
            className = callObj.split('.')[0]
            if className.endswith('()'):
                className = className[:-2]
            caller = modName+'.'+className

        return caller

    @staticmethod
    def getCaller(callLevel=2):
        """ Function to get the FQN of caller (FQN = module.class.function or module.function)
        :return: The name of the calling function
        """
        of = inspect.getouterframes(inspect.currentframe())[callLevel][0]
        try:
            callObj = of.f_locals['self']
            if isinstance(callObj, object):
                print('yes')
                try:
                    packageName = inspect.getattr_static(callObj, '__package__')
                except AttributeError:
                    packageName = None
                moduleName = inspect.getattr_static(callObj, '__module__')
                className = str(of.f_locals['self']).split('<')[1].split()[0].split()[0].split('.')[1]
                cs = inspect.stack()
                fxName = cs[callLevel][3]
                if packageName is not None:
                    caller = packageName+'.'+moduleName+'.'+className+'.'+fxName
                else:
                    caller = moduleName+'.'+className+'.'+fxName
            else:
                raise KeyError()
        except IndexError:
            caller = of.f_locals['self']
        except KeyError:
            cs = inspect.stack()
            callObj = cs[callLevel+1][4][0].split('=')[1].strip()
            dynMod = inspect.getmodule(callObj)
            dmm = inspect.getmembers(dynMod)
            try:
                packageName = inspect.getattr_static(dmm, '__package__')
            except AttributeError:
                packageName = None
            pathArray = str(cs[callLevel][1]).replace('/', '|').replace(path.sep, '|').split('|')
            modName = pathArray[len(pathArray) - 1].split('.')[0]
            className = callObj.split('.')[0]
            fxName = callObj.split('.')[1][:-2]
            if packageName is None:
                caller = modName+'.'+className+'.'+fxName
            else:
                caller = packageName+'.'+modName+'.'+className+'.'+fxName
            '''
            if caller == '<module>':
                caller = cs[callLevel][0].f_locals['__name__']
            caller = mod + '.' + caller
            '''

        return caller


class PlatformUtils:
    FileSep = path.sep
    EnvPathSep = pathsep

    @staticmethod
    def getPythonVersion():
        return str(sys.version_info[0]) + '.' + str(sys.version_info[1])


class ExceptionHelper(object):

    def __init__(self):
        pass
        #self.logger = AppLogger().getAppLibLogger(className='ExceptionHelper')

    def handleInputError(self, errorMessage: str):
        ieQuote = QuoteMachine().getRandonQuote(quoteType='INPUT_ERROR')
        self.Logger.console(ieQuote)
        raise ValueError(errorMessage)

    def handleError(self, errorMessage: str):
        errorQuote = QuoteMachine().getRandomQuote(quoteType='ERROR')
        self.Logger.info(errorQuote)
        self.Logger.console(errorQuote)
        self.Logger.error(errorMessage)
        raise RuntimeError(errorMessage)

    @staticmethod
    def getOffender():
        eType, eObj, eTable = sys.exc_info()
        eFrame = eTable.tb_frame
        eLine = str(eTable.tb_lineno)
        modName = eFrame.f_globals['__name__']
        return 'Module: '+modName+' Line: ' + eLine

    @staticmethod
    def printSimpleStacktrace():
        stack = traceback.format_exc().split('\n')
        for line in stack:
            if line.strip(' ').startswith('File'):
                rawName = line.strip('File ').split(',')[0].strip('"').split('/')
                modName = rawName[len(rawName) - 1].strip('.py')
                lineNum = line.strip('File ').split(',')[1].strip('line ')
                print('[' + modName + '][' + lineNum + ']')


class QuoteMachine:

    FinishedOpQuotes = [
        "Nice work man. Really, very impressive! \U0001f44d",
        "Sweet work, it's donut time. \U0001F369",
        "Operation was a success. You should quit while you are ahead and go home \U0001F3C3 \U0001F3DA"
    ]

    WrongInputQuotes = [
        "Um yeah, I'm going to have to have you correct your input value. \U0001F644",
        "Guess you are having a rough day. \U0001F60F Want to try a different input value this time? "
    ]

    ErrorQuotes = [
        "Looks like that didn't work so well. \U0001F615",
        "Dam, looks like today is going to be a long day! \U0001F613 "
    ]

    def getRandomQuote(self, quoteType):
        if quoteType.upper() == 'FINISHED':
            quote = self.FinishedOpQuotes[random.randint(0, len(self.FinishedOpQuotes) - 1)]
        elif quoteType.upper() == 'WRONG_INPUT':
            quote = self.FinishedOpQuotes[random.randint(0, len(self.FinishedOpQuotes) - 1)]
        elif quoteType.upper() == 'ERROR':
            quote = 'Aw Snap! ' + self.FinishedOpQuotes[random.randint(0, len(self.FinishedOpQuotes) - 1)]
        else:
            quote = "Mum is the word"

        return quote


class AppException(Exception, JsonObject):

    def __init__(self, errorMessage: str, errorCode: int = -100):
        self.ErrorCode = errorCode
        self.ErrorMessage = errorMessage


class FrameworkException(Exception, JsonObject):

    def __init__(self, errorMessage: str):
        self.message = errorMessage
        self.ErrorMessage = errorMessage
