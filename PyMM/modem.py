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
'''Implementation of the modem module'''

import dbus

from .sim import Sim
from enum import IntEnum, unique
from PyMM import ModemManagerBusName
from PyMM.bearer import Bearer


@unique
class ModemState(IntEnum):
    '''Enumeration which represents the current initialisation state of the modem. Corresponds
       verbatim to the values from https://www.freedesktop.org/software/ModemManager/api/latest/gdbus-org.freedesktop.ModemManager1.Modem.html#gdbus-property-org-freedesktop-ModemManager1-Modem.State.'''

    MM_MODEM_STATE_FAILED = -1,
    MM_MODEM_STATE_UNKNOWN = 0,
    MM_MODEM_STATE_INITIALIZING = 1,
    MM_MODEM_STATE_LOCKED = 2,
    MM_MODEM_STATE_DISABLED = 3,
    MM_MODEM_STATE_DISABLING = 4,
    MM_MODEM_STATE_ENABLING = 5,
    MM_MODEM_STATE_ENABLED = 6,
    MM_MODEM_STATE_SEARCHING = 7,
    MM_MODEM_STATE_REGISTERED = 8,
    MM_MODEM_STATE_DISCONNECTING = 9,
    MM_MODEM_STATE_CONNECTING = 10,
    MM_MODEM_STATE_CONNECTED = 11,


class Modem:
    '''Represents a single modem managed by the ModemManager service'''

    _modem_interface_name = 'org.freedesktop.ModemManager1.Modem'

    def __init__(self, system_bus, path, modem):
        self._system_bus = system_bus
        self._path = path

        if type(modem) is dbus.Dictionary:
            self._modem = modem[self._modem_interface_name]
            self._modem_object = self._system_bus.get_object(ModemManagerBusName, self._path)
        else:
            raise Exception()

    def __str__(self):
        return self._path

    def __repr__(self):
        return self._path

    @property
    def all_properties(self):
        return self._modem_object.GetAll(self._modem_interface_name,
                                         dbus_interface='org.freedesktop.DBus.Properties')

    @property
    def Manufacturer(self):
        return self.get_property('Manufacturer')

    @property
    def Model(self):
        return self.get_property('Model')

    @property
    def SignalQuality(self):
        return self.get_property('SignalQuality')

    @property
    def CarrierConfiguration(self):
        return self.get_property('CarrierConfiguration')

    @property
    def State(self):
        return ModemState(self.get_property('State'))

    @property
    def Sim(self):
        return Sim(self._system_bus, self.get_property('Sim'))

    @property
    def EquipmentIdentifier(self):
        return self.get_property('EquipmentIdentifier')

    @property
    def Bearers(self):
        return list(map(lambda x: Bearer(self._system_bus, x), self.get_property('Bearers')))

    @property
    def Drivers(self):
        return self.get_property('Drivers')

    def Reset(self):
        return self._modem_object.Reset(dbus_interface=self._modem_interface_name)

    def Enable(self, enable=True):
        return self._modem_object.Enable(enable, dbus_interface=self._modem_interface_name)

    def CreateBearer(self, props):
        print(props)
        return self._modem_object.CreateBearer(props, dbus_interface=self._modem_interface_name)

    def get_property(self, property_name):
        return self._modem_object.Get(self._modem_interface_name, property_name,
                                      dbus_interface='org.freedesktop.DBus.Properties')
