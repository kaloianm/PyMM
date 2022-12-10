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
import os
import logging

from curses import echo, wrapper
from PyMM import ModemManager
from PyMM.modem import ModemState


class ModemController:

    def __init__(self):
        self.mm = ModemManager()

        logging.info(f'Found Modem Manager: {self.mm} {self.mm.all_properties}')
        logging.info(f'Found {len(self.mm.managed_modems)} modems as {self.mm.managed_modems}:')

    def next(self):
        modem = next(iter(self.mm.managed_modems.values()))
        logging.info(f'''Modem {modem}:
                    Manufacturer: {modem.Manufacturer}
                    State: {modem.State.name} ({modem.State})
                    EquipmentIdentifier: {modem.EquipmentIdentifier}
                    Drivers: {modem.Drivers}
                    Bearers: {modem.Bearers}''')

        if modem.State == ModemState.MM_MODEM_STATE_FAILED:
            logging.info('Resetting modem because it is in state FAILED ...')
            modem.Reset()

            return True

        if modem.State == ModemState.MM_MODEM_STATE_REGISTERED:
            logging.info('Connecting modem ...')

            sim = modem.Sim
            logging.info(f'''Sim {sim}:
                    SimIdentifier: {sim.SimIdentifier}
                    Imsi: {sim.Imsi}
                    OperatorIdentifier: {sim.OperatorIdentifier}
                    OperatorName: {sim.OperatorName}''')

            if len(modem.Bearers) == 0:
                bearer = modem.CreateBearer({
                    'apn': 'telefonica.es',
                    'user': 'telefonica',
                    'password': 'telefonica'
                })
            else:
                bearer = modem.Bearers[0]

            if not bearer.Connected:
                bearer.Connect()

            return True

        if modem.State == ModemState.MM_MODEM_STATE_CONNECTED:
            bearer = modem.Bearers[0]

            logging.info(f'''Bearer {bearer}:
                        Connected: {bearer.Connected}
                        Interface: {bearer.Interface}
                        Ip4Config: {bearer.Ip4Config}''')

            return False

        logging.info('Completed')
        return False


class Controller:

    def __init__(self, window_title, modem):
        self._win = curses.newwin(curses.LINES - 1, curses.COLS - 1, 0, 0)
        self._modem = modem

        self._win.addstr(0, 0, window_title, curses.A_STANDOUT)


class SelectModem(Controller):

    def __init__(self, mm, current_modem):
        super().__init__('Select modem', current_modem)
        self._mm = mm

    def select(self):
        self._win.addstr(2, 1, '(P) Back to the previous menu')
        while True:
            key = self._win.getkey()
            if key == 'p' or key == 'P':
                return self._modem


class UnlockModem(Controller):

    def __init__(self, modem):
        super().__init__('Unlock modem', modem)

    def unlock(self):
        curses.echo()
        self._win.addstr(2, 0, 'Enter PIN: ')
        PIN = self._win.getstr(4).decode('utf-8')
        self._modem.Sim.SendPin(PIN)


class ReceivedSMS(Controller):

    def __init__(self, modem):
        super().__init__('Received SMS', modem)

    def show(self):
        self._win.addstr(2, 1, '(P) Back to the previous menu')
        while True:
            key = self._win.getkey()
            if key == 'p' or key == 'P':
                break


class SendSMS(Controller):

    def __init__(self, modem):
        super().__init__('Send SMS', modem)

    def show(self):
        self._win.addstr(2, 1, '(P) Back to the previous menu')
        while True:
            key = self._win.getkey()
            if key == 'p' or key == 'P':
                break


class Internet(Controller):

    def __init__(self, modem):
        super().__init__('Internet', modem)

    def show(self):
        self._win.addstr(2, 1, '(0) Connect')
        self._win.addstr(3, 1, '(1) Disconnect')
        self._win.addstr(4, 1, '(P) Back to the previous menu')
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


def wrapped_main(stdscr):
    '''Curses wrapped entrypoint for the application'''

    mm = ModemManager()
    logging.info(f'Found Modem Manager {mm} {mm.all_properties}')

    while True:
        stdscr.clear()

        stdscr.addstr(0, 0,
                      f'ModemManager {mm.Version} with {len(mm.managed_modems)} managed modems',
                      curses.A_BOLD)

        modem = None

        if len(mm.managed_modems) > 0:
            modem = list(mm.managed_modems.values())[0]
            stdscr.addstr(2, 0, f'Active modem (Press M to change, U to unlock): {modem}',
                          curses.A_BOLD)
            stdscr.addstr(3, 1, f'Manufacturer: {modem.Manufacturer}')
            stdscr.addstr(4, 1, f'State: {modem.State.name}')
            stdscr.addstr(5, 1, f'SIM IMEI: {modem.Sim.SimIdentifier}, SIM IMSI: {modem.Sim.Imsi}')

            stdscr.addstr(7, 0, f'Select an option from the menu:', curses.A_STANDOUT)

            stdscr.addstr(8, 1, '(0) Received SMS')
            stdscr.addstr(9, 1, '(1) Send SMS')
            stdscr.addstr(10, 1, '(2) Internet')
            stdscr.addstr(11, 1, '(E) Enable modem')
            stdscr.addstr(12, 1, '(R) Reset modem')

        stdscr.addstr(13, 1, '(Q) Quit')
        stdscr.refresh()

        key = stdscr.getkey()

        if modem:
            if key == 'm' or key == 'M':
                controller = SelectModem(mm, modem)
                modem = controller.select()
            if key == 'u' or key == 'U':
                controller = UnlockModem(modem)
                controller.unlock()
            if key == '0':
                controller = ReceivedSMS(modem)
                controller.show()
            if key == '1':
                controller = SendSMS(modem)
                controller.show()
            if key == '2':
                controller = Internet(modem)
                controller.show()
            if key == 'e' or key == 'E':
                modem.Enable(True)
            if key == 'r' or key == 'R':
                modem.Reset()

        if key == 'q' or key == 'Q':
            break


def script_main():
    '''Main entrypoint for the PyMMDemo application'''

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
    wrapper(wrapped_main)


if __name__ == '__main__':
    script_main()
