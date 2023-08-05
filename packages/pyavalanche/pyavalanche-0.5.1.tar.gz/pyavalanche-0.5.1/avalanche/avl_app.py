"""
This module implements classes and utility functions to manage Avalanche application.

:author: yoram@ignissoft.com
"""

from os import path
from random import randint
import shutil

from trafficgenerator.tgn_app import TgnApp

from avalanche.api.avl_tcl import AvlTclWrapper
from avalanche.avl_object import AvlObject
from avalanche.avl_project import AvlProject, AvlTest, AvlClient, AvlServer, AvlAssociation, AvlInterface
from avalanche.avl_hw import AvlHw, AvlPhyChassis, AvlPhyModule, AvlPhyPort


def init_avl(logger, tcl_lib_install_dir, avl_install_dir):
    """ Create Avalanche application object.

    :param logger: python logger object
    :param tcl_lib_install_dir: Tcllib directory
    :param avl_install_dir: Avalanche installation directory
    :return: Avalanche object
    """
    return AvlApp(logger, AvlTclWrapper(logger, tcl_lib_install_dir, avl_install_dir))


class AvlApp(TgnApp):
    """ TestCenter driver. Equivalent to TestCenter Application. """

    def __init__(self, logger, api_wrapper):
        """ Set all kinds of application level objects - logger, api, etc.

        :param logger: python logger (e.g. logging.getLogger('log'))
        :param api_wrapper: api wrapper object inheriting and implementing StcApi base class.
        """

        super(self.__class__, self).__init__(logger, api_wrapper)
        AvlObject.str_2_class = TYPE_2_OBJECT

        self.system = AvlObject(objType='system', objRef='system1', parent=None)
        self.system.system = self.system
        self.system.project = None
        self.system.api = self.api
        self.system.logger = self.logger

        self.hw = None
        self.project = None
        self.connected = False

    def connect(self):
        """ Login to Avalanche server.
        Login must be the first command.
        """

        self.api.avl_command('login {}'.format(randint(0, 999)))
        self.hw = self.system.get_child('PhysicalChassisManager')
        self.connected = True

    def disconnect(self):
        """ Disconnect from chassis and shutdown. """

        if self.hw:
            for chassis in self.hw.get_objects_by_type('PhysicalChassis'):
                self.api.avl_command("disconnect", chassis.get_attribute('IpAddress'))
        if self.connected:
            self.api.avl_command('logout', 'shutdown')
        self.connected = False

    def load_config(self, config_file_name):
        """ Load configuration file from tcc or xml.

        :param config_file_name: full path to the configuration file.
        """

        project_ref = self.api.perform('import ' + self.system.obj_ref(), File=path.normpath(config_file_name))
        self.project = AvlProject(parent=self.system, objRef=project_ref)
        self.project.project = self.project

    def save_config(self, config_file_name):
        """ Save configuration file as tcc or xml.

        :param config_file_name: full path to the configuration file.
        """

        self.api.perform('save ' + self.system.obj_ref())
        self.api.perform('export ' + self.system.obj_ref(), projectsTestsHandles=self.project.obj_ref())
        shutil.copy(self.system.get_attribute('latestExportedFile'), config_file_name)


TYPE_2_OBJECT = {'interface': AvlInterface,
                 'association': AvlAssociation,
                 'client': AvlClient,
                 'server': AvlServer,
                 'physicalchassismanager': AvlHw,
                 'physicalport': AvlPhyPort,
                 'physicaltestmodule': AvlPhyModule,
                 'test': AvlTest}
