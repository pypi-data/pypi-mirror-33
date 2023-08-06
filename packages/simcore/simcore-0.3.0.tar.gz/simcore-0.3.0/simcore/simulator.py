########################################################################
#
# simulator.py
#
# Copyright (C) 2018 Antonio Ceballos Roa
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

import abc

class Simulator():
    """Base class of a simulator

    This simulator includes:
      - a model of an environment
      - a model of a vehicle

    This is an abstract class that must be extended to implement
    a concrete simulator.
    """

    def __init__(self):
        self._env = self.create_env()
        self._vehicle = self.create_vehicle()
        self.__started = False

    @property
    def env(self):
        return self._env

    @property
    def vehicle(self):
        return self._vehicle

    @abc.abstractmethod
    def create_env(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_vehicle(self):
        raise NotImplementedError

    @abc.abstractmethod
    def vehicle_init_state(self):
        raise NotImplementedError

    @abc.abstractmethod
    def start_sim_submodels(self):
        pass

    @abc.abstractmethod
    def stop_sim_submodels(self):
        pass

    @abc.abstractmethod
    def step_sim_submodels(self, delta_simclock=1):
        pass

    def start(self):
        self._env.set_vehicle_state(self.vehicle_init_state())
        self.start_sim_submodels()
        self.__started = True

    def is_started(self):
        return self.__started

    def stop(self):
        self._env.stop()
        self.stop_sim_submodels()

    def step(self, delta_simclock=1):
        self._env.step(delta_simclock)
        self._vehicle.step(delta_simclock)
        self.step_sim_submodels(delta_simclock)
