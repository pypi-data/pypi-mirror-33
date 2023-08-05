"""
Classes and utilities to manage Avalanche HW.

:author: yoram@ignissoft.com
"""

from collections import OrderedDict

from avalanche.avl_object import AvlObject


class AvlHw(AvlObject):
    """ Represent STC port. """

    def get_chassis(self, hostname):
        for chassis in self.get_objects_or_children_by_type('PhysicalChassis'):
            if chassis.get_attribute('ipAddress') == hostname:
                return chassis
        connect_rc = self.api.avl_command('connect', hostname)
        return AvlPhyChassis(parent=self, objRef=connect_rc)


class AvlPhyBase(AvlObject):
    """ Base class for all Avalanche Physical sub-tree objects. """

    def get_inventory(self):
        self.attributes = self.get_attributes(*self.attributes_names)
        for child_var, child_type_index in self.children_types.items():
            child_type, child_index = child_type_index
            children = OrderedDict()
            for child in self.get_children(child_type):
                children[int(child.get_attribute(child_index))] = child
            setattr(self, child_var, children)
            for child in getattr(self, child_var).values():
                child.get_inventory()


class AvlPhyChassis(AvlPhyBase):
    """ Represent Avalanche physical chassis/appliance. """

    attributes_names = ('ActiveSoftware', 'Model', 'SerialNumber')
    children_types = {'modules': ('PhysicalTestModules', 'SlotNumber')}


class AvlPhyModule(AvlPhyBase):

    attributes_names = ()
    children_types = {'ports': ('Ports', 'PortNumber')}


class AvlPhyPort(AvlPhyBase):

    attributes_names = ('Location',)
    children_types = {}

    def reserve(self):
        self.api.avl_command('reserve', self.attributes['Location'])

    def release(self):
        self.api.avl_command('release', self.attributes['Location'])
