# -*- coding: utf-8 -*-
from collective.preventactions.testing import COLLECTIVE_PREVENTACTIONS_ROBOT_TESTING  # noqa
from plone.testing import layered

import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    robots_file = [
        'example.robot',
    ]

    for robot_file in robots_file:
        rts = robotsuite.RobotTestSuite(robot_file)
        suite.addTests([
            layered(rts, layer=COLLECTIVE_PREVENTACTIONS_ROBOT_TESTING)
        ])
    return suite
