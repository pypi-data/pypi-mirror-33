"""
:author: yoram@ignissoft.com
"""

from os import path
from sys import platform

from trafficgenerator.tgn_tcl import TgnTclWrapper, get_args_pairs, tcl_file_name, tcl_list_2_py_list


if platform == 'win32':
    app_subdir = 'Layer 4-7 Application/TclAPI'
else:
    # Not supported yet.
    app_subdir = None


class AvlTclWrapper(TgnTclWrapper):
    """ STC Python API over Tcl interpreter. """

    def __init__(self, logger, tcl_lib_install_dir, avl_install_dir, tcl_interp=None):
        super(self.__class__, self).__init__(logger, tcl_interp)
        tcl_lib_85_dir = tcl_file_name(path.join(tcl_lib_install_dir, 'tcl8.5'))
        self.eval('set auto_path [linsert $auto_path 0 {} {}]'.format(tcl_lib_install_dir, tcl_lib_85_dir))
        self.eval('lappend auto_path ' + tcl_file_name(path.join(avl_install_dir, app_subdir)))
        self.eval('package forget av')
        self.ver = self.eval('package require av')

    def avl_command(self, command, *attributes):
        return self.eval('av::' + command + ' ' + ' '.join(attributes))

    #
    # SpirentTestCenter Tcl package commands.
    #

    def config(self, obj_ref, **attributes):
        """ Set or modifies one or more object attributes, or a relation.

        :param obj_ref: requested object reference.
        :param attributes: dictionary of {attributes: values} to configure.
        """

        self.avl_command('config', obj_ref, get_args_pairs(attributes))

    def create(self, obj_type, parent, **attributes):
        """ Creates one or more Spirent TestCenter Automation objects.

        :param obj_type: object type.
        :param parent: object parent - object will be created under this parent.
        :param attributes: additional attributes.
        :return: STC object reference.
        """

        return self.avl_command('create ' + obj_type + ' -under ' + parent.obj_ref(),
                                get_args_pairs(attributes))

    def delete(self, obj_ref):
        """ Delete the specified object.

        :param obj_ref: object reference of the object to delete.
        """

        return self.avl_command('delete', obj_ref)

    def get(self, obj_ref, attribute=None):
        """ Returns the value(s) of one or more object attributes or a set of object handles.

        :param obj_ref: requested object reference.
        :param attribute: requested attribute. If empty - return values of all object attributes.
        :return: requested value(s) as returned by get command.
            If all attributes were requested the return value is dictionary
            {attrib_name:attrib_val, attrib_name:attrib_val, ..}
            If single attribute was requested, the returned value is simple str.
        """

        output = self.avl_command('get', obj_ref, '-' + attribute if attribute is not None else '')
        if attribute:
            return output
        attributes_dict = dict(zip(*[iter(tcl_list_2_py_list(output))] * 2))
        return dict(zip([s[1:] for s in attributes_dict.keys()], attributes_dict.values()))

    def getList(self, obj_ref, attribute):

        output = self.avl_command('get', obj_ref, '-' + attribute if attribute is not None else '')
        return tcl_list_2_py_list(output)

    def perform(self, command, **arguments):
        """ Execute a command.

        :param command: requested command.
        :param arguments: additional arguments.
        :return: value returned by 'perform command'.
        """

        return self.avl_command('perform', command, get_args_pairs(arguments))
