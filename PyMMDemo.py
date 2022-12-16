#!/usr/bin/env python3
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


class Screen:
    '''Represents a generic Screen functionality in the application.'''

    def __init__(self, screen_title, mm):
        self._win = curses.newwin(curses.LINES - 1, curses.COLS - 1, 0, 0)
        self._mm = mm
        self._current_row = 0

        self.add_row(0, screen_title, curses.A_BOLD)
        self.add_row(0, '')

    def add_row(self, indent, s, format=curses.A_NORMAL):
        self._win.addstr(self._current_row, indent, s, format)
        self._current_row += 1


class ModemScreen(Screen):
    '''Represents a specialisation of Screen which operates on a specific modem.'''

    def __init__(self, screen_title, mm, modem):
        super().__init__(screen_title, mm)
        self._modem = modem


class SelectModem(Screen):
    '''Screen which prompts the caller to select a modem from the set of available modems and
       returns the new selection. If (P) is pressed, returns current_modem.'''

    def __init__(self, mm, current_modem):
        super().__init__('Select modem', mm)
        self._current_modem = current_modem

    def select(self):
        self.add_row(1, '(P) Back to the previous menu')

        while True:
            key = self._win.getkey()
            if key == 'p' or key == 'P':
                return self._current_modem


class UnlockModem(ModemScreen):
    '''Screen which prompts the caller to unlock a locked modem by entering a PIN.'''

    def __init__(self, mm, modem):
        super().__init__('Unlock modem', mm, modem)

    def unlock(self):
        curses.echo()
        self.add_row(0, 'Enter PIN: ')
        PIN = self._win.getstr(4).decode('utf-8')
        self._modem.Sim.SendPin(PIN)


class ReceivedSMS(ModemScreen):
    '''Screen which shows the received SMS(s).'''

    def __init__(self, mm, modem):
        super().__init__('Received SMS', mm, modem)

    def show(self):
        self.add_row(1, '(P) Back to the previous menu')

        while True:
            key = self._win.getkey()
            if key == 'p' or key == 'P':
                break


class SendSMS(ModemScreen):
    '''Screen which allows an SMS to be sent.'''

    def __init__(self, mm, modem):
        super().__init__('Send SMS', mm, modem)

    def show(self):
        self.add_row(1, '(P) Back to the previous menu')

        while True:
            key = self._win.getkey()
            if key == 'p' or key == 'P':
                break


class Internet(ModemScreen):
    '''Screen to manage the internet connections of the modem.'''

    def __init__(self, mm, modem):
        super().__init__('Internet', mm, modem)

    def show(self):
        self.add_row(1, '(0) Connect')
        self.add_row(1, '(1) Disconnect')
        self.add_row(1, '(P) Back to the previous menu')

        while True:
            key = self._win.getkey()
            if key == '0':
                self.connect()
            if key == '1':
                self.disconnect()
            if key == 'p' or key == 'P':
                break

    def connect(self):
        pass

    def disconnect(self):
        pass


class MainScreen(Screen):
    '''The main screen of the application.'''

    def __init__(self, mm):
        super().__init__(f'ModemManager {mm.Version} with {len(mm.managed_modems)} managed modems',
                         mm)

        if len(mm.managed_modems) > 0:
            self._modem = list(mm.managed_modems.values())[0]
        else:
            self._modem = None

    def start(self):
        if self._modem:
            self.add_row(0, f'Active modem: {self._modem}', curses.A_BOLD)
            self.add_row(1, f'Manufacturer: {self._modem.Manufacturer}')
            self.add_row(1, f'State: {self._modem.State.name}')

            if self._modem.State > ModemState.MM_MODEM_STATE_INITIALIZING:
                self.add_row(1, f'Signal quality: {self._modem.SignalQuality}')
                self.add_row(1, f'Carrier configuration: {self._modem.CarrierConfiguration}')
                self.add_row(
                    1,
                    f'SIM IMEI: {self._modem.Sim.SimIdentifier}, SIM IMSI: {self._modem.Sim.Imsi}')

            self.add_row(1, '')

            self.add_row(0, f'Select an option from the menu:', curses.A_STANDOUT)
            self.add_row(0, '')

            self.add_row(1, '(0) Received SMS')
            self.add_row(1, '(1) Send SMS')
            self.add_row(1, '(2) Internet')
            self.add_row(1, '(M) Change active modem')
            self.add_row(1, '(U) Unlock PIN')
            self.add_row(1, '(E) Enable active modem')
            self.add_row(1, '(R) Reset active modem')

        self.add_row(1, '(Q) Quit')
        self.add_row(1, ' ')

        key = self._win.getkey()

        if self._modem:
            if key == 'm' or key == 'M':
                controller = SelectModem(self._mm, self._modem)
                self._modem = controller.select()
            if key == 'u' or key == 'U':
                controller = UnlockModem(self._mm, self._modem)
                controller.unlock()
            if key == '0':
                controller = ReceivedSMS(self._mm, self._modem)
                controller.show()
            if key == '1':
                controller = SendSMS(self._mm, self._modem)
                controller.show()
            if key == '2':
                controller = Internet(self._mm, self._modem)
                controller.show()
            if key == 'e' or key == 'E':
                self._modem.Enable(True)
            if key == 'r' or key == 'R':
                self._modem.Reset()

        if key == 'q' or key == 'Q':
            return True

        return False


def wrapped_main(stdscr, mm):
    '''Curses wrapped entrypoint for the application'''

    while True:
        stdscr.clear()

        main_screen = MainScreen(mm)
        if main_screen.start():
            break


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

    curses.wrapper(lambda stdscr: wrapped_main(stdscr, mm))


if __name__ == '__main__':
    application_main()
