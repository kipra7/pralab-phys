"""
LI5650 is a QCoDeS driver for the Stanford Research Systems NF Lock-in Amplifier.

Attributes:
    phase (Parameter): Phase of the signal in degrees.
    frequency (Parameter): Frequency of the signal in Hz.
    amplitude (Parameter): Amplitude of the signal in V.
    x_offset (Parameter): X-axis offset in percentage.
    y_offset (Parameter): Y-axis offset in percentage.
    reference (Parameter): Reference signal source.
    time_constant (Parameter): Time constant of the filter in seconds.
    input_gain (Parameter): Input gain in Ohms.
    source_frequency (Parameter): Source frequency in Hz.
    filter_slope (Parameter): Filter slope in dB/octave.
    ac_sensitivity (Parameter): Current sensitivity in A.
    v_sensitivity (Parameter): Voltage sensitivity in V.
    offset_status_x (Parameter): Status of X-axis offset (ON/OFF).
    offset_status_y (Parameter): Status of Y-axis offset (ON/OFF).

Methods:
    auto_all(): Automatically adjusts all settings.
    auto_phase(): Automatically adjusts the phase.
    auto_offset(): Automatically adjusts the offset.
    auto_time_constant(): Automatically adjusts the time constant.
    auto_sensitivity(): Automatically adjusts the sensitivity.
    reset(): Resets the instrument.
    disable_front_panel(): Disables the front panel.
    enable_front_panel(): Enables the front panel.
"""
from functools import partial
import numpy as np
from typing import Any

from qcodes import VisaInstrument
from qcodes.parameters import ArrayParameter, ParamRawDataType
from qcodes.utils.validators import Numbers, Ints, Enum, Strings

from typing import Tuple

class LI5650(VisaInstrument):
    """
    This is the qcodes driver for the Stanford Research Systems NF
    Lock-in Amplifier
    """

    def __init__(self, name: str, address: str, **kwargs: Any):
        super().__init__(name, address, **kwargs)

        # Reference and phase
        self.add_parameter('phase',
                           label='Phase',
                           get_cmd='PHAS?',
                           get_parser=float,
                           set_cmd='PHAS {:.2f}',
                           unit='deg',
                           vals=Numbers(min_value=-360, max_value=729.99))

 
        self.add_parameter('frequency',
                           label='Frequency',
                           get_cmd='FREQ?',
                           get_parser=float,
                           set_cmd='FREQ {:.4f}',
                           unit='Hz',
                           vals=Numbers(min_value=1e-3, max_value=11000e3))

        self.add_parameter('amplitude',
                           label='Amplitude',
                           get_cmd=':SOUR:VOLT?',
                           get_parser=float,
                           set_cmd=':SOUR:VOLT {:.3f}',
                           unit='V',
                           vals=Numbers(min_value=0, max_value=1000000))

        self.add_parameter('x_offset',
                           label='x_offset',
                           get_cmd=':CALCulate1:OFFSet?',
                           get_parser=float,
                           set_cmd=':CALCulate1:OFFSet {:.3f}',
                           unit='%',
                           vals=Numbers(min_value=0, max_value=100))

        self.add_parameter('y_offset',
                           label='y_offset',
                           get_cmd=':CALCulate2:OFFSet?',
                           get_parser=float,
                           set_cmd=':CALCulate2:OFFSet {:.3f}',
                           unit='%',
                           vals=Numbers(min_value=0, max_value=100))

        self.add_parameter('reference',
                           label='Reference',
                           get_cmd=':ROUT2?',
                           get_parser=str,
                           set_cmd=':ROUT2 {}',
                           vals=Enum("RINP", "IOSC", "SINP"))

        self.add_parameter('time_constant',
                           label='Time constant',
                           get_parser=float,
                           get_cmd=':FILT:TCON?',
                           set_cmd=':FILT:TCON {}',
                           unit='s')


        self.add_parameter('input_gain',
                           label='Input gain',
                           get_cmd=':INP:GAIN?',
                           get_parser=str,
                           set_cmd=':INP:GAIN {}',
                           unit='Ohm',
                           val_mapping={1: "IE6\n", 100: "IE8\n"})

        self.add_parameter('source_frequency',
                           label='Source frequency',
                           get_cmd=':SOUR:FREQ?',
                           get_parser=float,
                           set_cmd=':SOUR:FREQ {:.4f}',
                           unit='Hz',
                           vals=Numbers(min_value=5e-4, max_value=2.6e5))

        self.add_parameter('filter_slope',
                           label='Filter slope',
                           get_cmd=':FILT:SLOP?',
                           get_parser=int,
                           set_cmd=':FILT:SLOP {}',
                           unit='dB/oct',
                           vals=Enum(6, 12, 18, 24))

        self.add_parameter('ac_sensitivity',
                           label='Current Sensitivity',
                           get_cmd=':CURR:AC:RANG?',
                           get_parser=float,
                           set_cmd=':CURR:AC:RANG {}',
                           unit='A',
                           vals=Numbers(min_value=10e-15, max_value=1e-6))

        self.add_parameter('v_sensitivity',
                           label='Voltage Sensitivity',
                           get_cmd=':VOLT:AC:RANG?',
                           get_parser=float,
                           set_cmd=':VOLT:AC:RANG {}',
                           unit='V',
                           vals=Numbers(min_value=1e-9, max_value=1))


        # Aux input/output
        for i in [1, 2, 3, 4]:
            self.add_parameter(f'data{i}',
                               label=f'data {i}',
                               get_cmd=partial(self._get_data, i),
                               get_parser=float,
                               unit='')

                           
        self.add_parameter(name='offset_status_x',
                           get_cmd=':CALCulate1:OFFSet:STATe?',
                           set_cmd=':CALCulate1:OFFSet:STATe {}',
                           val_mapping={'OFF': 0,
                                        'ON': 1})
        
        self.add_parameter(name='offset_status_y',
                           get_cmd=':CALCulate2:OFFSet:STATe?',
                           set_cmd=':CALCulate2:OFFSet:STATe {}',
                           val_mapping={'OFF': 0,
                                        'ON': 1})
        # Auto functions
        self.add_function('auto_all', call_cmd=':SENS:AUTO:ONCE')
        self.add_function('auto_phase', call_cmd=':PHASe:AUTO:ONCE')
        self.add_function('auto_offset', call_cmd=':CALC1:OFFS:AUTO:ONCE')
        #self.add_function('auto_offset_x', call_cmd=':CALC1:OFFS:AUTO:ONCE')
        self.add_function('auto_time_constant', call_cmd=':SENS:FILT:AUTO:ONCE')
        self.add_function('auto_sensitivity', call_cmd=':SENSE:CURR:AC:RANG:AUTO:ONCE')
        # Interface
        self.add_function('reset', call_cmd='*RST')

        self.add_function('disable_front_panel', call_cmd='OVRM 0')
        self.add_function('enable_front_panel', call_cmd='OVRM 1')


    def _get_data(self, data_number):
        if data_number==1:
            self.write(':DATA 2')
        elif data_number==2:
            self.write(':DATA 4')
        elif data_number==3:
            self.write(':DATA 8')
        elif data_number==4:
            self.write(':DATA 16')
        return self.ask('FETC?')
