# Copyright 2022 Kaloian Manassiev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''Implementation of the Sim module'''

from PyMM import ModemManagerBusName


class Sim:
    '''Represents a single Sim card managed by a specific Modem'''

    _sim_interface_name = 'org.freedesktop.ModemManager1.Sim'

    def __init__(self, system_bus, sim_path):
        self._system_bus = system_bus
        self._path = sim_path
        self._sim_object = self._system_bus.get_object(ModemManagerBusName, self._path)

    def __str__(self):
        return f'Sim @ {self._path}'

    def __repr__(self):
        return f'Sim @ {self._path}'

    @property
    def SimIdentifier(self):
        return self.get_property('SimIdentifier')

    @property
    def Imsi(self):
        return self.get_property('Imsi')

    @property
    def OperatorIdentifier(self):
        return self.get_property('OperatorIdentifier')

    @property
    def OperatorName(self):
        return self.get_property('OperatorName')

    def SendPin(self, pin):
        return self._sim_object.SendPin(pin, dbus_interface=self._sim_interface_name)

    def get_property(self, property_name):
        return self._sim_object.Get(self._sim_interface_name, property_name,
                                    dbus_interface='org.freedesktop.DBus.Properties')
