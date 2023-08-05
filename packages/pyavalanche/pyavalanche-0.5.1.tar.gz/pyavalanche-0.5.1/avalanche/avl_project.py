"""
Classes and utilities to manage Avalanche project.
"""

import time

from avalanche.avl_object import AvlObject


class AvlProject(AvlObject):
    """ Represents Avalanche project object. """

    def __init__(self, **data):
        super(self.__class__, self).__init__(objType='project', **data)
        self.get_children('tests')

    @property
    def tests(self):
        return {test.name: test for test in self.get_objects_by_type('test')}


class AvlTest(AvlObject):
    """ Represents Avalanche test object. """

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.client = self.get_child('configuration.test.client')
        self.server = self.get_child('configuration.test.server')

    def start(self, trial=False, blocking=False):
        self.system.api.avl_command('apply', self.ref, '1' if trial else '0', '1')
        status = self.status()
        while status != 'TEST_RUNNING' and status != 'TEST_COMPLETED':
            time.sleep(1)
            status = self.status()
        if blocking:
            self.wait()

    def stop(self):
        self.command('stop {}'.format(self.system.ref), workspace=self.system.get_attribute('workspace'))
        self.wait()

    def wait(self):
        status = self.status()
        while status != 'TEST_COMPLETED':
            time.sleep(1)
            status = self.status()

    def status(self):
        return self.system.get_objects_or_children_by_type('runningtestinfo')[0].get_attribute('runningTestStatus')


class AvlCluster(AvlObject):
    """ Represents Avalanche cluster. """

    pass


class AvlClient(AvlCluster):
    """ Represents Avalanche client side. """

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.associations = self.get_children('globalassociations.association', 'userbasedassociations.association')


class AvlServer(AvlCluster):
    """ Represents Avalanche server side. """

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.associations = self.get_children('association')


class AvlAssociation(AvlObject):
    """ Represents Avalanche association. """

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.interface = self.get_child('associated_interface')

    def get_name(self):
        return int(self.get_attribute('id')) + 1


class AvlInterface(AvlObject):
    """ Represents Avalanche interface. """

    def set_port(self, location):
        self.set_attributes(port=location)
