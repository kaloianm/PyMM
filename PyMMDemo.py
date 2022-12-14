#! /usr/bin/env python3
#

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
'''Script which demonstrates the capabilities of the PyMM package'''

import curses
import dbus
import logging

from PyMM import ModemManager
from PyMM.modem import ModemState

###
### Infrastructure classes
###


class Screen:
    '''Represents a generic Screen functionality in the application.'''

    def __init__(self, screen_title, mm):
        self._win = curses.newwin(curses.LINES - 1, curses.COLS - 1, 0, 0)

        self._screen_title = screen_title
        self._mm = mm

        self._current_row = 0
        self._choices = {}

    def __show__(self):
        assert ('This method must not be reached')

    def add_row(self, indent, s, format=curses.A_NORMAL):
        self._win.addstr(self._current_row, indent, s, format)
        self._current_row += 1

    def add_choice(self, s, function, format=curses.A_NORMAL):
        shortcut = str(len(self._choices))
        self._choices[shortcut] = function

        self.add_row(1, f'({shortcut}) - {s}', format)

    def show(self):
        while True:
            self._win.clear()

            self._current_row = 0
            self._choices = {}

            self.add_row(0, self._screen_title, curses.A_BOLD)
            self.add_row(0, '')

            self.__show__()

            self.add_row(1, '')
            self.add_row(1, '(Q) - Quit / Previous')

            key = self._win.getkey()
            if key == 'q' or key == 'Q':
                break

            if key in self._choices:
                self._choices[key]()


class ModemScreen(Screen):
    '''Represents a specialisation of Screen which operates on a specific modem.'''

    def __init__(self, screen_title, mm, modem):
        super().__init__(screen_title, mm)
        self._modem = modem


###
### Specific screen implementations below
###


class SelectModem(Screen):
    '''Screen which prompts the caller to select a modem from the set of available modems and
       returns the new selection. If (P) is pressed, returns current_modem.'''

    def __init__(self, mm, current_modem):
        super().__init__('Select modem', mm)
        self._current_modem = current_modem

    def __show__(self):

        def select_modem(m):
            self._current_modem = m

        for modem in [None] + list(self._mm.managed_modems.values()):
            self.add_choice(modem, lambda modem=modem: select_modem(modem),
                            curses.A_BOLD if self.selected_modem == modem else curses.A_NORMAL)

    @property
    def selected_modem(self):
        return self._current_modem


class UnlockModem(ModemScreen):
    '''Screen which prompts the caller to unlock a locked modem by entering a PIN.'''

    def __init__(self, mm, modem):
        super().__init__('Unlock modem', mm, modem)

    def __show__(self):
        curses.echo()

        self.add_row(0, 'Enter PIN: ')
        PIN = self._win.getstr(4).decode('utf-8')
        self._modem.Sim.SendPin(PIN)


class ReceivedSMS(ModemScreen):
    '''Screen which shows the received SMS(s).'''

    def __init__(self, mm, modem):
        super().__init__('Received SMS', mm, modem)

    def __show__(self):
        self.add_row(1, '(P) Back to the previous menu')

        while True:
            key = self._win.getkey()
            if key == 'p' or key == 'P':
                break


class SendSMS(ModemScreen):
    '''Screen which allows an SMS to be sent.'''

    def __init__(self, mm, modem):
        super().__init__('Send SMS', mm, modem)

    def __show__(self):
        self.add_row(1, '(P) Back to the previous menu')

        while True:
            key = self._win.getkey()
            if key == 'p' or key == 'P':
                break


class Internet(ModemScreen):
    '''Screen to manage the internet connections of the modem.'''

    def __init__(self, mm, modem):
        super().__init__('Internet', mm, modem)
        self._modem_simple = modem.simple_interface

    def __show__(self):
        self.add_choice('Connect', lambda: self.connect())
        self.add_choice('Disconnect', lambda: self.disconnect())

    def connect(self):
        self._modem_simple.Connect({
            'apn': 'telefonica.es',
            'user': 'telefonica',
            'password': 'telefonica',
        })
        pass

    def disconnect(self):
        self._modem_simple.Disconnect()
        pass


class MainScreen(Screen):
    '''The main screen of the application.'''

    def __init__(self, stdscr, mm):
        super().__init__(f'ModemManager {mm.Version} with {len(mm.managed_modems)} managed modems',
                         mm)

        if len(mm.managed_modems) > 0:
            self._modem = list(mm.managed_modems.values())[0]
        else:
            self._modem = None

    def __show__(self):
        self.add_row(0, f'Active modem: {self._modem}', curses.A_BOLD)

        if self._modem:
            self.add_row(1, f'Manufacturer: {self._modem.Manufacturer}')
            self.add_row(1, f'State: {self._modem.State.name}')

            if self._modem.State > ModemState.MM_MODEM_STATE_INITIALIZING:
                self.add_row(1, f'Signal quality: {self._modem.SignalQuality}')
                self.add_row(1, f'Carrier configuration: {self._modem.CarrierConfiguration}')
                self.add_row(
                    1,
                    f'SIM IMEI: {self._modem.Sim.SimIdentifier}, SIM IMSI: {self._modem.Sim.Imsi}')

        self.add_row(0, '')
        self.add_row(0, 'Select an option from the menu:', curses.A_STANDOUT)
        self.add_row(0, '')

        def select_modem():
            selector = SelectModem(self._mm, self._modem)
            selector.show()

            self._modem = selector.selected_modem

        self.add_choice('Select modem', select_modem)

        if self._modem:
            self.add_choice('Unlock SIM', lambda: UnlockModem(self._mm, self._modem).show())
            self.add_choice('Send SMS', lambda: SendSMS(self._mm, self._modem).show())
            self.add_choice('Received SMS', lambda: ReceivedSMS(self._mm, self._modem).show())
            self.add_choice('Internet', lambda: Internet(self._mm, self._modem).show())
            self.add_choice('Enable active modem', lambda: self._modem.Enable())
            self.add_choice('Reset active modem', lambda: self._modem.Reset())
            self.add_choice('Refresh', lambda: None)


def application_main():
    '''Main entrypoint for the PyMMDemo application'''

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

    try:
        mm = ModemManager()
    except dbus.exceptions.DBusException:
        logging.exception(
            'Exception caught instantiating the ModemManager service. Most likely cause is that the service has not been started.'
        )
        return

    logging.info(f'Found {mm} {mm.all_properties}')

    curses.wrapper(lambda stdscr: MainScreen(stdscr, mm).show())


if __name__ == '__main__':
    application_main()
