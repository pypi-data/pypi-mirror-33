from pylegos.core import FileUtils
from pylegos.core import PlatformUtils
from pylegos.core import JsonConfig
from pylegos.utils import NameConverter
from pylegos.app_platform import CommandRunner

FSEP = PlatformUtils.FileSep


class ProjectService:

    def __init__(self, name):
        self.ProjectName = name
        self.AppName = name.lower()
        self.ProjectBaseDir = self.ProjectName+PlatformUtils.FileSep
        self.TemplateDir = FileUtils.getParentDir(__file__)+PlatformUtils.FileSep+'templates'+PlatformUtils.FileSep

    def __validate(self):
        if FileUtils.dirExists(self.ProjectName):
            raise RuntimeError('A project by that name already exists')

    def __buildDirTree(self):
        containerDirs = ['tests', 'app', 'bin', 'build']
        testDir = self.ProjectBaseDir+'tests'+FSEP
        appDirs = ['modules']
        FileUtils.createDir(self.ProjectName)
        for cDir in containerDirs:
            FileUtils.createDir(self.ProjectBaseDir+cDir)

        FileUtils.createDir(testDir+'app'+FSEP+'modules')

        for appDir in appDirs:
            FileUtils.createDir(self.ProjectBaseDir+'app'+FSEP+appDir)

    def __buildManifest(self):
        sep = PlatformUtils.FileSep
        sourceFile = self.TemplateDir+'config'+sep+'package.template'
        targetFile = self.ProjectBaseDir+sep+'package.json'
        FileUtils.copyFile(sourceFile, targetFile)
        fileContents = open(sourceFile, 'r').read()
        fileContents = fileContents.replace('{{APP_NAME}}', self.AppName)
        targetFileObj = open(targetFile, 'w')
        targetFileObj.write(fileContents)
        targetFileObj.close()

    def __buildConfFile(self):
        sep = PlatformUtils.FileSep
        appDir = self.ProjectBaseDir+'app'+sep
        FileUtils.copyFile(self.TemplateDir+'config'+sep+'app.ini', appDir+'conf'+sep+self.AppName+'.ini')

    def __buildCodeFiles(self):
        sep = PlatformUtils.FileSep
        appDir = self.ProjectBaseDir+sep+'app'+sep
        appName = self.ProjectName.lower()
        templateFiles = FileUtils().getFileMatches(self.TemplateDir+'code'+sep, 'app*.tpl')
        for tf in templateFiles:
            file = open(self.TemplateDir+'code'+sep+tf, 'r')
            fileContent = file.read()
            file.close()
            fileContent = fileContent.replace('{{APPNAME_OBJECT}}', NameConverter.getObjectName(self.AppName))
            codeFile = open(appDir+tf.replace('app', self.AppName).replace('.tpl', '.py'), 'w')
            codeFile.write(fileContent)
            codeFile.close()

    def __buildAppBinFile(self):
        sep = PlatformUtils.FileSep
        appName = self.ProjectName.lower()
        tplFile = 'app.sh'
        FileUtils.copyFile(self.TemplateDir+'launchers'+sep+tplFile, self.ProjectBaseDir+'bin'+sep+appName)

    def __buildTestFiles(self):
        sep = PlatformUtils.FileSep
        appDir = self.ProjectBaseDir+'test'+sep+'app'+sep
        testFiles = ['test_'+self.AppName+'.py', 'test_'+self.AppName+'_controllers.py', 'test_'+self.AppName+'_services.py']
        for tf in testFiles:
            testFile = open(appDir+tf, 'w')
            testFile.write('from unittest import TestCase\n\n')
            testFile.close()

    def __copyModDefTemplate(self):
        s = PlatformUtils.FileSep
        FileUtils.copyFile(self.TemplateDir+'config'+s+'modelDef.tpl', self.ProjectBaseDir+'build'+s+'def-files'+s+'model.def')
        FileUtils.copyFile(self.TemplateDir+'config'+s+'model-def.README', self.ProjectBaseDir+'build'+s+'def-files'+s+'model-def.README')

    def __createDatabaseScripts(self):
        s = PlatformUtils.FileSep

        objectScripts = ['dblinks.sql',
                         'synonyms.sql',
                         'sequences.sql',
                         'types.sql',
                         'queues.sql',
                         'tables.sql',
                         'triggers.sql',
                         'views.sql',
                         'indexes.sql',
                         'constraints_ck.sql',
                         'constraints_pk.sql',
                         'constraints_uk.sql',
                         'constraints_fk.sql']
        dataScripts = ['seed.sql']

        for obj in objectScripts:
            FileUtils.touchFile(self.ProjectBaseDir+'app'+s+'database'+s+'ddl'+s+'objects'+s+obj)

        for data in dataScripts:
            FileUtils.touchFile(self.ProjectBaseDir+'app'+s+'database'+s+'data'+s+data)

        FileUtils.copyFile(self.TemplateDir+'config'+s+'database-userInfo.tpl', self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_info.ini')
        FileUtils.copyFile(self.TemplateDir+'config'+s+'database-userPrivs.tpl', self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_privs.ini')
        # REPLACE TOKENS IN INFO FILE
        iniFile = open(self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_info.ini', 'r')
        fileContents = iniFile.read()
        iniFile.close()
        fileContents = fileContents.replace('{{APPNAME}}', self.AppName.upper())
        iniFile = open(self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_info.ini', 'w')
        iniFile.write(fileContents)
        iniFile.close()
        # REPLACE TOKENS IN PRIV FILE
        iniFile = open(self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_privs.ini', 'r')
        fileContents = iniFile.read()
        iniFile.close()
        fileContents = fileContents.replace('{{APPNAME}}', self.AppName.upper())
        iniFile = open(self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_privs.ini', 'w')
        iniFile.write(fileContents)
        iniFile.close()

    def __createBuildFiles(self):
        s = PlatformUtils.FileSep
        FileUtils.copyFile(self.TemplateDir+'code'+s+'build.py', self.ProjectBaseDir+'build'+s+'build.py')

    def initProject(self):
        self.__validate()
        self.__buildDirTree()
        self.__buildManifest()
        #self.__buildCodeFiles()
        #self.__buildConfFile()
        #self.__buildTestFiles()
        #self.__copyModDefTemplate()
        #self.__createDatabaseScripts()
        #self.__createBuildFiles()
        FileUtils.changeWorkingDir(self.ProjectBaseDir)
        CommandRunner().run('git init')


class ModuleService:

    def __init__(self, moduleName):
        fsep = PlatformUtils.FileSep
        self.ModuleName = moduleName.lower()
        self.ProjectBaseDir = FileUtils.getWorkingDir()+fsep
        projectDirArray = self.ProjectBaseDir.strip(fsep).split(fsep)
        self.ProjectName = projectDirArray[len(projectDirArray)-1].lower()
        self.ModuleBaseDir = 'app'+fsep+'modules'+fsep
        self.ModuleDir = self.ModuleBaseDir+self.ModuleName+fsep
        self.ConfDir = 'app'+fsep+'conf'+fsep
        self.TemplateDir = FileUtils.getParentDir(__file__)+fsep+'templates'+fsep

    def __validate(self):
        if not FileUtils.dirExists(self.ModuleBaseDir):
            message = """ It does not appear you are in your project directory.  This command must be run from within your project directory.
            If you are inside your project directory, then you are getting this error because your project was not initialized as modular. To
            make it modular.  Navigate to your project base directory and run the following:
            
            pylegos project modularize --name <project name>
            
            """
            raise RuntimeError(message)

    def __buildModDir(self):
        FileUtils.createDir(self.ModuleBaseDir+self.ModuleName)

    def __buildManifest(self):
        fsep = PlatformUtils.FileSep
        manifestFilename = self.ProjectBaseDir+'app'+fsep+'conf'+fsep+self.ModuleName.lower()+'_manifest.ini'
        FileUtils.copyFile(self.TemplateDir+'modBaseManifest.tpl', manifestFilename)
        manFile = open(manifestFilename, 'r')
        fileContents = manFile.read()
        manFile.close()
        fileContents = fileContents.replace('{{MODNAME}}', self.ModuleName.lower())
        manFile = open(manifestFilename, 'w')
        manFile.write(fileContents)
        manFile.close()

    def __buildConfFile(self):
        FileUtils.copyFile(self.TemplateDir+'module.ini', self.ConfDir+self.ModuleName+'.ini')

    def __buildCodeFiles(self):
        templateFiles = FileUtils().getFileMatches(self.TemplateDir, 'module_*.tpl')
        for tpl in templateFiles:
            codeFilename = self.ModuleDir+tpl.replace('module', self.ModuleName).replace('.tpl', '.py')
            FileUtils.copyFile(self.TemplateDir+tpl, codeFilename)
            codeFile = open(codeFilename, 'r')
            fileContents = codeFile.read()
            codeFile.close()
            fileContents = fileContents.replace('{{MODNAME_OBJECT}}', NameConverter.getObjectName(self.ModuleName))
            fileContents = fileContents.replace('{{MODNAME}}', NameConverter.getObjectName(self.ModuleName))
            codeFile = open(codeFilename, 'w')
            codeFile.write(fileContents)
            codeFile.close()

    def __buildTestFiles(self):
        fsep = PlatformUtils.FileSep
        modTestDir = self.ProjectBaseDir+'test'+fsep+'app'+fsep+'modules'+fsep+self.ModuleName+fsep
        FileUtils.createDir(modTestDir)
        FileUtils.touchFile(modTestDir+'test_'+self.ModuleName+'.py')
        FileUtils.touchFile(modTestDir+'test_'+self.ModuleName+'_controllers.py')
        FileUtils.touchFile(modTestDir+'test_'+self.ModuleName+'_services.py')

    def __registerToManifest(self):
        fsep = PlatformUtils.FileSep
        manFilename = self.ProjectBaseDir+'conf'+fsep+self.ProjectName+'_manifest.ini'
        confManager = JsonConfig(configFile=manFilename)
        modArray = confManager.getKey('MODULES')
        modArray.append(self.ModuleName)
        confManager.setValue('MODULES', 'ModuleList', modArray)
        confManager.save()

    def initModule(self):
        self.__validate()
        self.__buildModDir()
        self.__buildCodeFiles()
        self.__buildTestFiles()


class GitService:

    def __init__(self):
        sep = PlatformUtils.FileSep
        self.ProjectDir = FileUtils.getWorkingDir()+sep
        if not FileUtils().dirExists(self.ProjectDir+'app'):
            raise RuntimeError('You must be inside your project to run git operations')

    def getTagCommit(self, tagName):
        # git show-ref -s <tag name>
        pass

    def __genDiff(self):
        pass

    def initProject(self):
        cmd = 'git init'
        CommandRunner().run(command=cmd)

    def createReleaseBranch(self, modName=None, fromBranch=None):
        if modName is not None:
            modConfFilename = self.ProjectDir+'app'+FSEP+'conf'+modName+'.ini'
            config = JsonConfig(configFile=modConfFilename)
            modVerInfo = config.getKey(keyName='module')
            majVer = modVerInfo['MAJOR']
            minVer = modVerInfo['MINOR']
            newMaj = float(majVer)+.1
            branchName = 'release-'+modName+'-'
        cmd = 'git branch'

    def createHotFixBranch(self):
        pass

