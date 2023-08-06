#!/usr/bin/env python3

########################################################################
#
# test_suite_simcore.py
#
# Copyright (C) 2018, Antonio Ceballos Roa
#
#   This file is part of Simcore.
#
#   Simcore is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Simcore is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Simcore.  If not, see <https://www.gnu.org/licenses/>.
#
########################################################################

import unittest
import argparse

from modules import simcore

import test_model
import test_env
import test_vehicle
import test_simulator

all_tests = False

def parse_args():
    global all_tests
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", help="run all tests", action="store_true")
    args = parser.parse_args()
    if args.all:
        print("Run all tests")
        all_tests = True

def suite():
    """Test suite for simcore
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(test_model.TestModel))
    test_suite.addTest(unittest.makeSuite(test_env.TestEnv))
    test_suite.addTest(unittest.makeSuite(test_vehicle.TestVehicle))
    test_suite.addTest(unittest.makeSuite(test_simulator.TestSimulator))
    if all_tests:
        pass
    return test_suite

if __name__ == '__main__':
    parse_args()
    runner = unittest.TextTestRunner()
    runner.run(suite())
