########################################################################
#
# test_env.py
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

from simcore import env

class TestEnv(unittest.TestCase):
    """
    Unit test for env.py
    """

    class _ConcreteEnv(env.Env):
        def step(self, deltatime=1):
            pass
        def set_vehicle_state(self, state):
            pass

    def setUp(self):
        self._anenv = TestEnv._ConcreteEnv()

    def tearDown(self):
        pass

    def test_env_is_abstract(self):
        with self.assertRaises(TypeError):
            abcenv = env.Env()

    def test_concrete_env(self):
        anotherenv = TestEnv._ConcreteEnv()

    def test_step(self):
        self._anenv.step()
        self._anenv.step(2)

    def test_step(self):
        self._anenv.step()
        self._anenv.step(2)
