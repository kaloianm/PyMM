# PyMM - Python ModemManager
Python module implementing an object-oriented front to the [ModemManager](https://www.freedesktop.org/wiki/Software/ModemManager/) [D-Bus API](https://www.freedesktop.org/software/ModemManager/doc/latest/ModemManager/ref-dbus.html).

# Requirements
* ModemManager version [1.20.0](https://gitlab.freedesktop.org/mobile-broadband/ModemManager/-/tree/1.20.0) or newer (otherwise, some of the APIs will result in a "method not found" error)
* libdbus library [1.15.0](https://gitlab.freedesktop.org/dbus/dbus/-/tree/dbus-1.15.2) or newer
