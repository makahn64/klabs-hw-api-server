# -*- coding: utf-8 -*-
"""Waveshare_ADDA - Python module for interfacing with the Waveshare AD/DA Pi HAT board
bus based analog-to-digital converters with the Raspberry Pi.




"""

import sys
from time import sleep
import pigpio as io
from drivers.DAC8552_PiGPIO import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K
from drivers.ADS1256_definitions import *
from drivers.ADS1256_PiGPIO import ADS1256
from drivers.waveshare_definitions import *

class WAVESHARE_ADDA(object):

    @property
    def adc(self):
        return self._adc

    @property
    def dac(self):
        return self._dac

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value

    def __init__(self, pi_host='klabs.local', skip_cal=False):

        self.pi = io.pi(pi_host)
        self._dac = DAC8552(pi=self.pi)
        self._adc = ADS1256(pi=self.pi)
        self._verbose = False

        if not skip_cal:
            self._adc.cal_self()

    def voltage_from_ADC(self, adval):
        pct = adval / 0x7fffff
        return 5.0 * pct

    # The * makes all params required to be named
    def seek_voltage(self, *, dac_output=DAC_A, feedback_input=EXT0, target_v, delta_v,  start_min = 0x0, start_max = 0xffff, start_point = 0x7ff):
        left = start_min
        right = start_max
        cursor = start_point

        while True:
            self._dac.write_dac(dac_output, cursor)
            sleep(.25)
            readVHex = self._adc.read_oneshot(feedback_input)
            readV = self.voltage_from_ADC(readVHex)
            if self._verbose:
                print("Read ", readV, "with cursor at", hex(cursor))
            deltaV = readV - target_v
            if self._verbose:
                print("Delta", self.voltage_from_ADC(readV))
            if abs(deltaV) < delta_v:
                break
            if left == cursor or right == cursor:
                break
            if deltaV > 0:
                right = cursor
                cursor = right - int((right - left) / 2)
            else:
                left = cursor
                cursor = left + int((right - left) / 2)

        return readV, cursor

    def seek_voltage_auto(self,*, dac_output=DAC_A, feedback_input=EXT0, target_v, delta_v):
        spoint = int((target_v / 0.1)*ONE_HUNDRED_MV_INCREMENT)
        smax = int(spoint*1.1)
        smin = int(spoint*0.9)
        return self.seek_voltage(dac_output=dac_output, feedback_input=feedback_input,
                                 target_v=target_v, start_point=spoint, start_max=smax, start_min=smin, delta_v=delta_v)

    def seek_voltage_auto_A(self,*, target_v, delta_v):
        return self.seek_voltage_auto(target_v=target_v, delta_v=delta_v)

    def seek_voltage_auto_B(self,*, target_v, delta_v):
        return self.seek_voltage_auto(target_v=target_v, delta_v=delta_v, dac_output=DAC_B, feedback_input=EXT1)

    def read_voltage(self, input_pin):
        hexValue = self._adc.read_oneshot(input_pin)
        voltage = self.voltage_from_ADC(hexValue)
        return voltage, hexValue

    def read_all(self):
        sequence = [AD_CHANNEL_MAP['0'],
                    AD_CHANNEL_MAP['1'],
                    AD_CHANNEL_MAP['2'],
                    AD_CHANNEL_MAP['3'],
                    AD_CHANNEL_MAP['4'],
                    AD_CHANNEL_MAP['5'],
                    AD_CHANNEL_MAP['6'],
                    AD_CHANNEL_MAP['7']
                    ]
        hexValues = self._adc.read_sequence(sequence)
        rval = []
        for hexVal in hexValues:
            voltage = self.voltage_from_ADC(hexVal)
            rval.append((voltage, hexVal))
        return rval

    def close(self):
        self.pi.stop()

