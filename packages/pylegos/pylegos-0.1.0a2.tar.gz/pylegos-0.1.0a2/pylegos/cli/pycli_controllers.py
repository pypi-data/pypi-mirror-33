from pylegos.cli.pycli_services import ProjectService
from pylegos.cli.pycli_services import ModuleService
from pylegos.app_platform import CommandError
from pylegos.app_platform import CommandRunner
from pylegos.core import FileUtils


class ProjectController:

    def __init__(self, projectName):
        self.ProjectName = projectName
        self.Service = ProjectService(name=self.ProjectName)

    def initProject(self):
        self.Service.initProject()

    def modularize(self):
        self.Service.modularize()


class ModuleController:

    def __init__(self, moduleName):
        self.ModuleName = moduleName.lower()
        self.Service = ModuleService(moduleName=self.ModuleName)

    def addModule(self):
        self.Service.initModule()


class GitController:

    def createBranch(self, type, targetOption, moduleName=None, baseBranch=None):
        pass

    def finalizeBranch(self):
        pass


class BuildController:

    @staticmethod
    def run():
        sep = PlatformProperty.FileSep
        projectBaseDir = FileUtils().getWorkingDir() + sep
        if FileUtils().dirExists(projectBaseDir+'app'):
            cmd = 'build/build.py'
            try:
                CommandRunner().run(command=cmd)
            except CommandError as ce:
                print(ce.message)
                exit(1)
        else:
            raise RuntimeError('You need to be at the top level directory of your project "project_base", when running build option')


