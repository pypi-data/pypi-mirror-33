########################################################################
#
# test_vehicle.py
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

from simcore import vehicle

class TestVehicle(unittest.TestCase):
    """
    Unit test for vehicle.py
    """

    class _ConcreteVehicle(vehicle.Vehicle):
        def step(self, deltatime=1):
            pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_vehicle_is_abstract(self):
        with self.assertRaises(TypeError):
            abcvehicle = vehicle.Vehicle()

    def test_concrete_vehicle(self):
        avehicle = TestVehicle._ConcreteVehicle()

    def test_step(self):
        avehicle = TestVehicle._ConcreteVehicle()
        avehicle.step()
        avehicle.step(2)
