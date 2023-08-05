"""
Avalanche package tests that require actual Avalanche chassis/appliance and active ports.

Test setup:
Two Avalanche ports connected back to back.

@author yoram@ignissoft.com
"""

from os import path
import json

from avalanche.avl_statistics_view import AvlClientStats
from avalanche.test.test_base import AvlTestBase


class AvlTestOnline(AvlTestBase):

    ports = []

    def test_inventory(self):
        """ Get chassis inventory. """
        self.logger.info(AvlTestOnline.test_inventory.__doc__.strip())

        ip, module, port = self.config.get('Client', 'association_1').split('/')
        chassis = self.avl.hw.get_chassis(ip)
        chassis.get_inventory()
        print chassis.modules
        print chassis.modules[int(module)].ports

    def test_reserve_ports(self):
        """ Load configuration on ports and verify that ports are online. """
        self.logger.info(AvlTestOnline.test_inventory.__doc__.strip())

        self.avl.load_config(path.join(path.dirname(__file__), 'configs/test_config.spf'))
        self._reserve_ports(self.config.get('Client', 'association_1'),
                            self.config.get('Server', 'association_1'))
        self.avl.project.tests['Test'].client.associations[0].interface.set_port(self.config.get('Client', 'association_1'))
        self.avl.project.tests['Test'].server.associations[0].interface.set_port(self.config.get('Server', 'association_1'))

    def test_run_wait(self):
        """ Load configuration on ports, run test and wait for test to complete. """
        self.logger.info(AvlTestOnline.test_inventory.__doc__.strip())

        self.test_reserve_ports()

        client_stats = AvlClientStats(self.avl.project, 'http')
        client_stats.read_stats()
        print(json.dumps(client_stats.statistics, indent=2))
        self.avl.project.tests['Test'].start(trial=True, blocking=True)
        client_stats.read_stats()
        print(json.dumps(client_stats.statistics, indent=2))

    def test_run_stop(self):
        """ Load configuration on ports, run test and wait for test to complete. """
        self.logger.info(AvlTestOnline.test_inventory.__doc__.strip())

        self.test_reserve_ports()
        self.avl.project.tests['Test'].start(trial=True)
        self.avl.project.tests['Test'].stop()

    def _reserve_ports(self, *locations):
        chassis_list = []
        for location in locations:
            ip, module, port = location.split('/')
            chassis = self.avl.hw.get_chassis(ip)
            if chassis not in chassis_list:
                chassis.get_inventory()
                chassis_list.append(chassis)
            chassis.modules[int(module)].ports[int(port)].reserve()
