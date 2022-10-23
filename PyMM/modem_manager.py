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
'''Implementation of the modem_manager module'''

import dbus

from .modem import Modem
from PyMM import ModemManagerBusName


class ModemManager:
    '''The top-level class serving as root for interaction with the ModemManager D-Bus service'''

    _modem_manager_interface_name = 'org.freedesktop.ModemManager1'

    def __init__(self):
        self._system_bus = dbus.SystemBus()
        self._modem_manager_object = self._system_bus.get_object(ModemManagerBusName,
                                                                 '/org/freedesktop/ModemManager1')

    def __str__(self):
        return f'ModemManager'

    def __repr__(self):
        return f'ModemManager'

    @property
    def all_properties(self):
        return self._modem_manager_object.GetAll(self._modem_manager_interface_name,
                                                 dbus_interface='org.freedesktop.DBus.Properties')

    @property
    def managed_modems(self):
        '''Returns a dictionary of the modems that are managed by this object.'''

        managed_objects = self._modem_manager_object.GetManagedObjects(
            dbus_interface='org.freedesktop.DBus.ObjectManager')

        return dict(
            map(lambda x: (x[0], Modem(self._system_bus, x[0], x[1])), managed_objects.items()))

    @property
    def Version(self):
        return self.get_property('Version')

    def get_property(self, property_name):
        return self._modem_manager_object.Get(self._modem_manager_interface_name, property_name,
                                              dbus_interface='org.freedesktop.DBus.Properties')
