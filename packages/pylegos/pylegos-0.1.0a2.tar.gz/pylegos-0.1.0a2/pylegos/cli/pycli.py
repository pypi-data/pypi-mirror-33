import argparse
import os
from argparse import Namespace
from pylegos.pylegos_properties import Properties
from pylegos.cli.pycli_controllers import ProjectController
from pylegos.cli.pycli_controllers import ModuleController
from pylegos.core import ExceptionHelper


class CommonUtils:

    @staticmethod
    def getBaseDir():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CliArgs(object):

    def __init__(self):
        self.AppName = 'pylegos'
        self.Version = Properties.Version

    def parse(self):

        runParser = argparse.ArgumentParser(description=self.AppName)
        runParser.add_argument('--version', '-v', action="version", version="Version: " + self.Version, help='Displays the version of the program')

        actionParser = runParser.add_subparsers(title='Actions', dest='action', description='Available actions')
        newActionParser = actionParser.add_parser('new', aliases=['n'])
        targetParser = newActionParser.add_subparsers(dest='newType')
        projectParser = targetParser.add_parser('project', aliases=['proj', 'p'])
        moduleParser = targetParser.add_parser('module', aliases=['mod', 'm'])
        projectParser.add_argument('projectName', help='Name of the project')
        moduleParser.add_argument('moduleName', help="name of the module to add")

        return runParser.parse_args()


def console(msg: str) -> None:
    print('::| '+str(msg))


def main():

    cliArgs = CliArgs().parse()
    runInIDE = False
    if runInIDE:
        cliArgs = Namespace(newType='project',
                            projectName='FooProj',
                            action='new',
                            projectModular=False,
                            projectInitModuleList=None,
                            debug=True)

    try:
        if cliArgs.action.lower() in ['new', 'n']:
            if cliArgs.newType in ['project', 'proj', 'p']:
                projectName = cliArgs.projectName
                console('Creating new project '+str(projectName))
                controller = ProjectController(projectName=projectName)
                controller.initProject()
                console('Project created.  Next step')
                console('')
                console('\t cd '+projectName)
                console('\t pylegos start')
                console('')
            elif cliArgs.newType in ['module', 'mod', 'm']:
                modName = cliArgs.moduleName
                print('Creating new module '+str(modName))
    except Exception as e:
            print('ERROR: '+str(e))
            #eh = ExceptionHelper()
            #eh.printSimpleStacktrace()
            #print('Error Line: '+str(eh.getOffender()))


if __name__ == '__main__':
    main()
