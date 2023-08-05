"""
Avalanche package tests that can run in offline mode.

@author yoram@ignissoft.com
"""

from os import path

from avalanche.test.test_base import AvlTestBase


class AvlTestOffline(AvlTestBase):

    def testLoadConfig(self):
        """ Load existing configuration. """
        self.logger.info(AvlTestOffline.testLoadConfig.__doc__.strip())

        self.avl.load_config(path.join(path.dirname(__file__), 'configs/test_config.spf'))
        file_name, file_ext = path.splitext(path.join(path.dirname(__file__), 'configs/test_config.spf'))
        self.avl.save_config(file_name + '-save' + file_ext)

    def testAnalyzeConfig(self):
        """ Analyze existing configuration. """
        self.logger.info(AvlTestOffline.testAnalyzeConfig.__doc__.strip())

        self.avl.load_config(path.join(path.dirname(__file__), 'configs/test_config.spf'))
        assert(len(self.avl.project.tests) == 3)
