"""
Classes and utilities to manage STC statistics views.
"""

from avalanche.avl_object import AvlObject


class AvlStats(object):
    """ Represents statistics view. """

    statistics = {}

    def __init__(self, project, side, view):
        """ Subscribe to view with default configuration type as defined by config_2_type.

        :param project: parent project object for all statistics.
        :param side: client/server.
        :param view: statistics view to subscribe to.
        """

        super(AvlStats, self).__init__()
        self.project = project
        if view:
            self.subscribe(side, view)
        self.statistics = {}

    def subscribe(self, side, view):
        """ Subscribe to statistics view.

        :param side: client/server.
        :param view: statistics view to subscribe to.
        """

        rds = self.project.api.avl_command('subscribe', side, '{}*'.format(view))
        self.rds = AvlObject(ObjType='ResultDataSet', parent=self.project, objRef=rds)

    def unsubscribe(self):
        """ UnSubscribe from statistics view. """

        self.project.api.unsubscribe(self.rds.ref)

    def read_stats(self):
        """ Reads the statistics view from Avalanche and saves it in statistics dictionary. """

        resultdataobjects = self.rds.get_objects_or_children_by_type('resultdataobjects')[0]
        self.statistics = resultdataobjects.get_attributes()


class AvlClientStats(AvlStats):

    def __init__(self, project, view):
        """ Subscribe to client view.

        :param project: parent project object for all statistics.
        :param view: client statistics view to subscribe to.
        """
        super(AvlClientStats, self).__init__(project, 'client', view)


class AvlServerStats(AvlStats):

    def __init__(self, project, view):
        """ Subscribe to server view.

        :param project: parent project object for all statistics.
        :param view: server statistics view to subscribe to.
        """

        super(AvlClientStats, self).__init__(project, 'server', view)
