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
'''Implementation of the Bearer module'''

from PyMM import ModemManagerBusName


class Bearer:
    '''Represents a single Bearer managed by a specific Modem'''

    _bearer_interface_name = 'org.freedesktop.ModemManager1.Bearer'

    def __init__(self, system_bus, bearer_path):
        self._system_bus = system_bus
        self._path = bearer_path
        self._bearer_object = self._system_bus.get_object(ModemManagerBusName, self._path)

    def __str__(self):
        return f'Bearer @ {self._path}'

    def __repr__(self):
        return f'Bearer @ {self._path}'

    @property
    def Connected(self):
        return self.get_property('Connected')

    @property
    def Interface(self):
        return self.get_property('Interface')

    @property
    def Ip4Config(self):
        return self.get_property('Ip4Config')

    def Connect(self):
        return self._bearer_object.Connect(dbus_interface=self._bearer_interface_name)

    def get_property(self, property_name):
        return self._bearer_object.Get(self._bearer_interface_name, property_name,
                                       dbus_interface='org.freedesktop.DBus.Properties')
