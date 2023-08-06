########################################################################
#
# test_simulator.py
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

from simcore import simulator
from simcore import env
from simcore import vehicle

class TestSimulator(unittest.TestCase):
    """
    Unit test for simulator.py
    """

    class _ConcreteSimulator(simulator.Simulator):

        class _ConcreteEnv(env.Env):
            def step(self, deltatime=1):
                pass
            def set_vehicle_state(self, state):
                pass
            def stop(self):
                pass

        class _ConcreteVehicle(vehicle.Vehicle):
            def step(self, deltatime=1):
                pass

        def create_env(self):
            return self._ConcreteEnv()

        def create_vehicle(self):
            return self._ConcreteVehicle()

        def vehicle_init_state(self):
            pass

        def start_sim_submodels(self):
            pass

        def step_sim_submodels(self, delta_simclock=1):
            pass

        def stop_sim_submodels(self):
            pass

    def setUp(self):
        self._sim = self._ConcreteSimulator()

    def tearDown(self):
        pass

    def test_simulator_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            abcsimulator = simulator.Simulator()

    def test_concrete_simulator(self):
        self._sim.env
        self._sim.vehicle
        self.assertFalse(self._sim.is_started())

    def test_start(self):
        self._sim.start()
        self.assertTrue(self._sim.is_started())

    def test_stop(self):
        self._sim.stop()
        self.assertFalse(self._sim.is_started())

    def test_step(self):
        self._sim.step()
        self._sim.step(2)
