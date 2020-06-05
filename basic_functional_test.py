from drivers.Waveshare_ADDA import WAVESHARE_ADDA
from drivers.waveshare_definitions import *

ws = WAVESHARE_ADDA()

ws.verbose = True
ws.seek_voltage_auto_A(target_v=1.0, delta_v=0.0001)

voltage, hexValue  = ws.read_voltage(EXT3)
print("Read", hex(hexValue), "which is", voltage, "volts.")

ws.close()